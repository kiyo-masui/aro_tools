
# File format parameters
HEADER_LEN = 12       # Bytes: index, loops, n_FFT_int
FRAME_HEADER_LEN = 8  # Bytes: FGPA counts, Unix_time
DTYPE = np.uint32

# Acquisition parameters
NTIME_RECORD = 1024     # Post integration, post-scrunch. Arbitrary, doesn't matter
FFT_RATE = 800e6 / 1024 / 2   # Hz

NFREQ = 1024
FREQ0 = 800.
DELTA_F = -400. / 1024

NPOL = 2

CAL_PERIOD_SAMPLES = 0


# Run parameters:

SAFETY_INTEG = 2048


class PowerDataRing(object):

    def __init__(self, filename, scrunch=1):

        self._filename = filename
        self._scrunch = scrunch

        with open(filename, r) as f:
            s = f.read(HEADER_LEN)
            f.seek(0, 2)
            size = f.tell()

        ring_bytes = size - HEADER_LEN
        integ_bytes = (FRAME_HEADER_LEN + NFREQ * NPOL * DTYPE.itemsize)
        self._ninteg_ring = ring_bytes // integ_bytes
        if ring_bytes % integ_bytes:
            raise RuntimeError('Odd filesize.')

        header = np.fromstring(s, DTYPE)
        self._sample_time = arr[2] / FFT_RATE
        self._delta_t = self._sample_time * scrunch
        self._record_offset = ((arr[0] + arr[1] * self._ninteg_ring)
                               // (scrunch * NTIME_RECORD))


    def current_records(self):
        ninteg_ring = self._ninteg_ring
        with open(self._filename, r) as f:
            s = f.read(HEADER_LEN)
        header = np.fromstring(s, DTYPE)
        index = header[0]
        loops = header[1]
        last_record = ((index + loops * ninteg_ring)
                       // (self._scrunch * NTIME_RECORD)
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
        parameters['nrecords'] = self._get_nrecords(filename)

        return parameters


