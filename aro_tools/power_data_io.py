import time

import numpy as np

# File format parameters
HEADER_LEN = 12       # Bytes: index, loops, n_FFT_int
FRAME_HEADER_LEN = 8  # Bytes: FGPA counts, Unix_time
DTYPE = np.dtype(np.uint32)

# Acquisition parameters
NTIME_RECORD = 1024     # Post integration, post-scrunch. Arbitrary, doesn't matter
FFT_RATE = 800e6 / 1024 / 2   # Hz

NFREQ = 1024
FREQ0 = 800.
DELTA_F = -400. / 1024

NPOL = 2
POL_WEIGHTS = [0., 1.]

CAL_PERIOD_SAMPLES = 0



class Ring(object):

    def __init__(self, filename, scrunch=1):

        self._filename = filename
        self._scrunch = scrunch

        with open(filename, 'r') as f:
            s = f.read(HEADER_LEN)
            f.seek(0, 2)
            size = f.tell()

        ring_bytes = size - HEADER_LEN
        integ_bytes = (FRAME_HEADER_LEN + NFREQ * NPOL * DTYPE.itemsize)
        self._ninteg_ring = ring_bytes // integ_bytes
        if ring_bytes % integ_bytes:
            raise RuntimeError('Odd filesize.')

        header = np.fromstring(s, DTYPE)
        self._sample_time = header[2] / FFT_RATE
        self._delta_t = self._sample_time * scrunch
        # The record we will call "0".
        # XXX
        self._record_offset = ((header[0] + int((header[1] - 0.4) * self._ninteg_ring))
                               // (scrunch * NTIME_RECORD))
        #self._record_offset = ((header[0] + header[1] * self._ninteg_ring)
        #                       // (scrunch * NTIME_RECORD))


    def current_records(self):
        ninteg_ring = self._ninteg_ring
        with open(self._filename, 'r') as f:
            s = f.read(HEADER_LEN)
        header = np.fromstring(s, DTYPE)
        index = header[0]
        loops = header[1]
        last_record = ((index + loops * ninteg_ring)
                       // (self._scrunch * NTIME_RECORD) + 1)
        last_record -= self._record_offset
        nrecord_ring = ninteg_ring // (self._scrunch * NTIME_RECORD)
        # The latest 80% of the ring is availble, for safety.
        first_available_record = last_record - int(nrecord_ring * 0.8)

        return first_available_record, last_record


    def get_parameters(self):

        parameters = {}

        parameters['cal_period_samples'] = CAL_PERIOD_SAMPLES
        parameters['delta_t'] = self._delta_t
        parameters['nfreq'] = NFREQ
        parameters['freq0'] = FREQ0

        parameters['delta_f'] = DELTA_F
        parameters['ntime_record'] = NTIME_RECORD
        parameters['nrecords'] = self.current_records()[1]

        return parameters


    def read_records(self, start_record=None, end_record=None):

        first_available_record, last_record = self.current_records()

        if start_record is None:
            start_record = first_available_record
        if end_record is None:
            end_record = last_record

        if start_record < first_available_record:
            raise DataGone()
        if end_record > last_record:
            end_record = last_record
        if start_record >= last_record:
            raise ValueError("No data to read.")

        scrunch = self._scrunch

        out = np.empty((NFREQ, (end_record - start_record), NTIME_RECORD),
                       dtype=np.float32)
        integ_bytes = NPOL * NFREQ * DTYPE.itemsize

        with open(self._filename, 'r') as f:
            for ii in range(end_record - start_record):
                abs_record_ind = ii + start_record + self._record_offset
                record_data = np.zeros((NTIME_RECORD, NFREQ), dtype=np.float32)
                for jj in range(NTIME_RECORD):
                    integ_ind_jj = (abs_record_ind * NTIME_RECORD + jj) * scrunch
                    for kk in range(self._scrunch):
                        integ_ind = (integ_ind_jj + kk) % self._ninteg_ring
                        f.seek(HEADER_LEN + integ_ind * integ_bytes)
                        s = f.read(integ_bytes)
                        integ = np.fromstring(s, dtype=DTYPE)
                        integ.shape = (NPOL, NFREQ)
                        for pp in range(NPOL):
                            record_data[jj, :] += integ[pp]
                out[:,ii,:] = np.transpose(record_data)
        out.shape = (NFREQ, (end_record - start_record) * NTIME_RECORD)
        return out



class DataGone(Exception):
    pass



MOCK_N_SAMP_INTEG = 512
MOCK_RING_LEN = 200
MOCK_START_TIME = time.time() - MOCK_RING_LEN

class MockRing(object):

    def __init__(self, filename, scrunch):
        self._scrunch = scrunch
        self._delta_t = MOCK_N_SAMP_INTEG * self._scrunch / FFT_RATE


    def get_parameters(self):
        parameters = {}

        parameters['cal_period_samples'] = CAL_PERIOD_SAMPLES
        parameters['delta_t'] = self._delta_t
        parameters['nfreq'] = NFREQ
        parameters['freq0'] = FREQ0

        parameters['delta_f'] = DELTA_F
        parameters['ntime_record'] = NTIME_RECORD
        parameters['nrecords'] = self.get_nrecords()

        return parameters


    def read_records(self, start_record=None, end_record=None):
        """Right now just generates fake data."""
        
        first_available_record, last_record = self.current_records()

        if start_record is None:
            start_record = first_available_record
        if end_record is None:
            end_record = last_record

        if start_record < first_available_record:
            raise DataGone()
        if end_record > last_record:
            end_record = last_record
        if start_record >= last_record:
            raise ValueError("No data to read.")

        nrecords = end_record - start_record
        ntime = nrecords * NTIME_RECORD
        out = np.empty((NFREQ, nrecords, NTIME_RECORD), dtype=np.float32)

        # The fake part.
        from numpy import random
        # Every record is the same!
        noise = random.randn(NTIME_RECORD, 2, NFREQ)
        record_data = (noise + 32) * 10
        record_data = record_data.astype(np.uint32)
        for ii in range(nrecords):
            out[:,ii,:] = np.transpose(record_data[:,0,:] + record_data[:,1,:])
        out.shape = (NFREQ, nrecords * NTIME_RECORD)
        return out


    def get_nrecords(self):
        """Totally fake."""

        last = int((time.time() - MOCK_START_TIME) / (self._delta_t * NTIME_RECORD))
        #print last
        return last

    def current_records(self):
        last = self.get_nrecords()
        first = last - int(MOCK_RING_LEN / self._delta_t / NTIME_RECORD)

        return first, last

