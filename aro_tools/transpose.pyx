"""Transpose algorigms."""

import numpy as np

cimport numpy as np
cimport cython


np.import_array()


# Prototypes of functions from ctranspose.c
cdef extern int simple_transpose(void *A, void *B, int lda, int ldb,
                                 int elem_size)
cdef extern int blocked_transpose(void *A, void *B, int lda, int ldb,
                                  int block_size, int elem_size)
cdef extern int blocked_transpose_memcpy(void *A, void *B, int lda, int ldb,
                                   int block_size, int elem_size)
cdef extern int blocked_transpose_SSE_32(void *A, void *B, int lda, int ldb,
                                        int block_size)
cdef extern int blocked_transpose_AVX_64(void *A, void *B, int lda, int ldb,
                                        int block_size)


def _setup_arr(arr):
    shape = arr.shape
    if len(shape) != 2:
        msg = "Expected a 2D array, got shape: %s." % repr(shape)
        raise ValueError(msg)
    if not arr.flags['C_CONTIGUOUS']:
        msg = "Input array must be C-contiguouse."
        raise ValueError(msg)
    lda, ldb = shape
    dtype = arr.dtype
    itemsize = dtype.itemsize
    out = np.empty((ldb, lda), dtype=dtype)
    return out, lda, ldb, itemsize


def simple(np.ndarray arr not None):
    """Transpose array using simple algorithm."""

    cdef np.ndarray out
    out, lda, ldb, itemsize = _setup_arr(arr)
    cdef void* arr_ptr = <void*> arr.data
    cdef void* out_ptr = <void*> out.data
    err = simple_transpose(arr_ptr, out_ptr, lda, ldb, itemsize)
    if err:
        msg = "Failed. Error code %d."
        raise ValueError(msg % err)
    return out


def blocked_memcpy(np.ndarray arr not None, block_size=32):
    """Transpose an array using blocked algorithm.

    Use ``memcpy`` to copy the elements.  This should always be slower than
    :fun:`blocked`. The function is mostly here for profiling.

    """

    cdef np.ndarray out
    out, lda, ldb, itemsize = _setup_arr(arr)
    cdef void* arr_ptr = <void*> arr.data
    cdef void* out_ptr = <void*> out.data
    err = blocked_transpose_memcpy(arr_ptr, out_ptr, lda, ldb, block_size,
                                   itemsize)
    if err:
        msg = "Failed. Error code %d."
        raise ValueError(msg % err)
    return out


def blocked(np.ndarray arr not None, block_size=32):
    """Transpose array using blocked algorithm."""

    cdef np.ndarray out
    out, lda, ldb, itemsize = _setup_arr(arr)
    cdef void* arr_ptr = <void*> arr.data
    cdef void* out_ptr = <void*> out.data
    err = blocked_transpose(arr_ptr, out_ptr, lda, ldb, block_size, itemsize)
    if err:
        msg = "Failed. Error code %d."
        raise ValueError(msg % err)
    return out


def blocked_SSE(np.ndarray arr not None, block_size=32):
    """Transpose array using blocked algorithm and SSE instruction set.

    """

    cdef np.ndarray out
    out, lda, ldb, itemsize = _setup_arr(arr)

    if arr.dtype.itemsize != 4 and arr.dtype.itemsize != 8:
        msg = "Require 4 or 8 byte elements, got %s." % repr(arr.dtype)
        raise ValueError(msg)

    cdef void* arr_ptr = <void*> arr.data
    cdef void* out_ptr = <void*> out.data
    if itemsize == 4:
        err = blocked_transpose_SSE_32(arr_ptr, out_ptr, lda, ldb, block_size)
    elif itemsize == 8:
        err = blocked_transpose_AVX_64(arr_ptr, out_ptr, lda, ldb, block_size)
    if err:
        msg = "Failed. Error code %d."
        raise ValueError(msg % err)
    return out

