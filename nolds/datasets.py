# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *
import numpy as np
import pkg_resources
import datetime


def fbm(n, H=0.75):
  """
  Generates fractional brownian motions of desired length.

  Author:
    Christian Thomae

  References:
    .. [fbm_1] https://en.wikipedia.org/wiki/Fractional_Brownian_motion#Method_1_of_simulation

  Args:
    n (int):
      length of sequence to generate
  Kwargs:
    H (float):
      hurst parameter

  Returns:
    array of float:
      simulated fractional brownian motion
  """
  # TODO more detailed description of fbm
  assert H > 0 and H < 1

  def R(t, s):
    twoH = 2 * H
    return 0.5 * (s**twoH + t**twoH - np.abs(t - s)**twoH)
  # form the matrix tau
  gamma = R(*np.mgrid[0:n, 0:n])  # apply R to every element in matrix
  w, P = np.linalg.eigh(gamma)
  L = np.diag(w)
  sigma = np.dot(np.dot(P, np.sqrt(L)), np.linalg.inv(P))
  v = np.random.randn(n)
  return np.dot(sigma, v)


def fgn(n, H=0.75):
  """
  Generates fractional gaussian noise of desired length.

  References:
    .. [fgn_1] https://en.wikipedia.org/wiki/Fractional_Brownian_motion

  Args:
    n (int):
      length of sequence to generate

  Kwargs:
    H (float):
      hurst parameter

  Returns:
    array of float:
      simulated fractional gaussian noise
  """
  return np.diff(fbm(n+1, H=H))


def qrandom(n):
  """
  Creates an array of n true random numbers obtained from the quantum random
  number generator at qrng.anu.edu.au

  This function requires the package quantumrandom and an internet connection.

  Args:
    n (int):
      length of the random array

  Return:
    array of ints:
      array of truly random unsigned 16 bit int values
  """
  import quantumrandom
  return np.concatenate([
    quantumrandom.get_data(data_type='uint16', array_length=1024)
    for i in range(int(np.ceil(n/1024.0)))
  ])[:n]


def load_qrandom():
  """
  Loads a set of 10000 random numbers generated by qrandom.

  This dataset can be used when you want to do some limited tests with "true"
  random data without an internet connection.

  Returns:
    int array
      the dataset
  """
  fname = "datasets/qrandom.npy"
  with pkg_resources.resource_stream(__name__, fname) as f:
    return np.load(f)


def load_brown72():
  """
  Loads the dataset brown72 with a prescribed Hurst exponent of 0.72

  Source: http://www.bearcave.com/misl/misl_tech/wavelets/hurst/

  Returns:
    float array:
      the dataset
  """
  fname = "datasets/brown72.npy"
  with pkg_resources.resource_stream(__name__, fname) as f:
    return np.load(f)


def tent_map(x, steps, mu=2):
  """
  Generates a time series of the tent map.

  Characteristics and Background:
    The name of the tent map is derived from the fact that the plot of x_i vs
    x_i+1 looks like a tent. For mu > 1 one application of the mapping function
    can be viewed as stretching the surface on which the value is located and
    then folding the area that is greater than one back towards the zero. This
    corresponds nicely to the definition of chaos as expansion in one dimension
    which is counteracted by a compression in another dimension.

  Calculating the Lyapunov exponent:
    The lyapunov exponent of the tent map can be easily calculated as due to
    this stretching behavior a small difference delta between two neighboring
    points will indeed grow exponentially by a factor of mu in each iteration.
    We thus can assume that:

    delta_n = delta_0 * mu^n

    We now only have to change the basis to e to obtain the exact formula that
    is used for the definition of the lyapunov exponent:

    delta_n = delta_0 * e^(ln(mu) * n)

    Therefore the lyapunov exponent of the tent map is:

    lambda = ln(mu)

  References:
    .. [tm_1] https://en.wikipedia.org/wiki/Tent_map

  Args:
    x (float):
      starting point
    steps (int):
      number of steps for which the generator should run

  Kwargs:
    mu (int):
      parameter mu that controls the behavior of the map

  Returns:
    generator object:
      the generator that creates the time series
  """
  for _ in range(steps):
    x = mu * x if x < 0.5 else mu * (1 - x)
    yield x

# TODO should all math be formatted like this, or should the documentation of
# logistic_map revert to a version that is more readable as plain text


def logistic_map(x, steps, r=4):
  r"""
  Generates a time series of the logistic map.

  Characteristics and Background:
    The logistic map is among the simplest examples for a time series that can
    exhibit chaotic behavior depending on the parameter r. For r between 2 and
    3, the series quickly becomes static. At r=3 the first bifurcation point is
    reached after which the series starts to oscillate. Beginning with r = 3.6
    it shows chaotic behavior with a few islands of stability until perfect
    chaos is achieved at r = 4.

  Calculating the Lyapunov exponent:
    To calculate the "true" Lyapunov exponent of the logistic map, we first
    have to make a few observations for maps in general that are repeated
    applications of a function to a starting value.

    If we have two starting values that differ by some infinitesimal
    :math:`delta_0` then according to the definition of the lyapunov exponent
    we will have an exponential divergence:

    .. math::
      |\delta_n| = |\delta_0| e^{\lambda n}

    We can now write that:

    .. math::
      e^{\lambda n} = \lim_{\delta_0 -> 0} |\frac{\delta_n}{\delta_0}|

    This is the definition of the derivative :math:`\frac{dx_n}{dx_0}` of a
    point :math:`x_n` in the time series with respect to the starting point
    :math:`x_0` (or rather the absolute value of that derivative). Now we can
    use the fact that due to the definition of our map as repetitive
    application of some f we have:

    .. math::
      f^{n\prime}(x) = f(f(f(...f(x_0)...))) = f'(x_n-1) \cdot f'(x_n-2)
      \cdot ... \cdot f'(x_0)

    with

    .. math::
      e^{\lambda n} = |f^{n\prime}(x)|

    we now have

    .. math::

      e^{\lambda n} &= |f'(x_n-1) \cdot f'(x_n-2) \cdot ... \cdot f'(x_0)| \\
      \Leftrightarrow \\
      \lambda n &= \ln |f'(x_n-1) \cdot f'(x_n-2) \cdot ... \cdot f'(x_0)| \\
      \Leftrightarrow \\
      \lambda &= \frac{1}{n} \ln |f'(x_n-1) \cdot f'(x_n-2) \cdot ... \cdot f'(x_0)| \\
             &= \frac{1}{n} \sum_{k=0}^{n-1} \ln |f'(x_k)|

    With this sum we can now calculate the lyapunov exponent for any map.
    For the logistic map we simply have to calculate :math:`f'(x)` and as we
    have

    .. math::
      f(x) = r x (1-x) = rx - rx²

    we now get

    .. math::
      f'(x) = r - 2 rx



  References:
    .. [lm_1] https://en.wikipedia.org/wiki/Tent_map
    .. [lm_2] https://blog.abhranil.net/2015/05/15/lyapunov-exponent-of-the-logistic-map-mathematica-code/

  Args:
    x (float):
      starting point
    steps (int):
      number of steps for which the generator should run

  Kwargs:
    r (int):
      parameter r that controls the behavior of the map

  Returns:
    generator object:
      the generator that creates the time series
  """
  for _ in range(steps):
    x = r * x * (1 - x)
    yield x


def load_financial():

  def load_finance_yahoo_data(f):
    f.readline()
    days = []
    values = []
    for l in f:
      fields = l.decode("utf-8")
      fields = fields.split(",")
      d = datetime.datetime.strptime(fields[0], "%Y-%m-%d")
      v = [np.nan if x.strip() == "null" else float(x) for x in fields[1:]]
      days.append(d)
      values.append(v)
    return np.array(days), np.array(values)

  def pad_opening_values(values):
    # fill first value from future if required
    first = 0
    while np.isnan(values[first, 0]):
      first += 1
    values[0, 0] = values[first, 0]
    # iterate over all indices where data is missing
    for i in np.where(np.isnan(values[:, 0]))[0]:
      j = i
      # pad opening value with close value of previous data
      while np.isfinite(values[j][0]):
        j -= 1
      values[i, 0] = values[j, 3]

  data = []
  for index in ["^JKSE", "^N225", "^NDX"]:
    fname = "datasets/{}.csv".format(index)
    with pkg_resources.resource_stream(__name__, fname) as f:
      days, values = load_finance_yahoo_data(f)
      pad_opening_values(values)
      data.append((days, values))
  return data


def barabasi1991_fractal(size, iterations, b1=0.8, b2=0.5):
  def b1991(x0, y0, w, h):
    if h < 0:
      # for a segment with negative slope we have flip the x-axis
      d, nxtp = b1991(x0, y0 + h, w, -h)
      return d[::-1], nxtp
    x1 = x0 + w // 4
    x2 = x0 + w // 2
    x3 = x2 + w // 4
    x4 = x0 + w
    data = np.zeros(w, dtype=np.float64)
    data[x0 - x0:x1 - x0] = np.linspace(0, 1, x1 - x0) * b1 * h + y0
    data[x1 - x0:x2 - x0] = np.linspace(1, 0, x2 - x1) * b1 * h + y0
    data[x2 - x0:x3 - x0] = np.linspace(0, 1, x3 - x2) * b2 * h + y0
    data[x3 - x0:x4 - x0] = np.linspace(0, 1, x4 - x3) * (1 - b2) * h \
                          + y0 + b2 * h
    return data, [x0, x1, x2, x3, x4]
  fractal = np.linspace(0, 1, size)
  intervals = [(0, size)]
  for _ in range(iterations):
    print(intervals)
    next_intervals = []
    for x1, x2 in intervals:
      d, nxtp = b1991(x1, fractal[x1], x2 - x1, fractal[x2-1] - fractal[x1])
      fractal[x1:x2] = d
      next_intervals.extend([(np1, np2) for np1, np2 in zip(nxtp[:-1], nxtp[1:])])
    intervals = next_intervals
  return fractal


brown72 = load_brown72()
jkse, n225, ndx = load_financial()
