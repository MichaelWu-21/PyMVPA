#!/usr/bin/env python
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the PyMVPA package for the
#   copyright and license terms.
#
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""
Monte-Carlo testing of Classifier-based Analyses
================================================

.. index:: statistical testing, monte-carlo, permutation

It is often desirable to be able to make statements like *"Performance is
significantly above chance-level"*.  PyMVPA supports *NULL* (aka *H0*)
hypothesis testing for :ref:`transfer errors <transfer_error>` and all
:ref:`dataset measures <chap_measures>`. In both cases the object computing the
measure or transfer error takes an optional constructor argument `null_dist`.
The value of this argument is an instance of some
:class:`~mvpa.clfs.stats.NullDist` estimator.  If *NULL* distribution is
luckily a-priori known, it is possible to reuse any distribution specified in
`scipy.stats` module. If the parameters of the distribution are known, such
distribution instance can be used to initialize FixedNullDist_ instance to be
specified in `null_dist` parameter.

However, as with other applications of statistics in classifier-based analyses
there is the problem that we do not know the distribution of a variable like
error or performance under the *NULL* hypothesis to assign the adored p-values,
i.e. the probability of a result given that there is no signal. Even worse, the
chance-level or guess probability of a classifier depends on the content of a
validation dataset, e.g. balanced or unbalanced number of samples per label and
total number of labels).

One approach to deal with this situation is to estimate the *NULL*
distribution.  A generic way to do this are permutation tests (aka *Monte
Carlo*, :ref:`Nichols et al. (2006) <NH02>`). Then *NULL* distribution is
estimated by computing some measure multiple times using datasets with no
relevant signal in them. These datasets are generated by permuting the labels
of all samples in the training dataset each time the measure is computed, and
therefore randomizing/removing any possible relevant information.

Given the measures computed using the permuted datasets one can now determine
the probability of the empirical measure (i.e. the one computed from the
original training dataset) under the *no signal* condition. This is simply the
fraction of measures from the permutation runs that is larger or smaller than
the emprical (depending on whether on is looking at performances or errors).

If the family of the distribution is known (e.g. Gaussian/Normal) and provided
in `dist_class` parameter of MCNullDist, then permutation tests done by
MCNullDist_ allow to determine the distribution parameters. Under strong
assumption of Gaussian distribution, 20-30 permutations should be sufficient to
get sensible estimates of the distribution parameters.  If no distribution
family can be assumed, with a larger number of permutations, derivation of CDF
out of population is possible with Nonparametric_ probability function (which
is the default value of `dist_class` for MCNullDist_).  If `null_dist` is
provided, the respective :class:`~mvpa.clfs.transerror.TransferError` or
:class:`~mvpa.measures.base.DatasetMeasure` instance will automatically use it
to estimate the *NULL* distribution and store the associated *p*-values in a
conditional attribute named `null_prob`.


.. _Distribution: api/mvpa.clfs.stats.NullDist-class.html
.. _Nonparametric: api/mvpa.clfs.stats.Nonparametric-class.html
.. _MCNullDist: api/mvpa.clfs.stats.MCNullDist-class.html
.. _FixedNullDist: api/mvpa.clfs.stats.FixedNullDist-class.html
"""

# lazy import
from mvpa.suite import *

# enable progress output for MC estimation
if __debug__:
    debug.active += ["STATMC"]

# some example data with signal
train = normal_feature_dataset(perlabel=50, nlabels=2, nfeatures=3,
                             nonbogus_features=[0,1], snr=0.3, nchunks=1)

# define class to estimate NULL distribution of errors
# use left tail of the distribution since we use MeanMatchFx as error
# function and lower is better
# in a real analysis the number of permutations should be larger
# to get stable estimates
terr = TransferError(clf=SMLR(),
                     null_dist=MCNullDist(permutations=100,
                                          tail='left'))

# compute classifier error on training dataset (should be low :)
err = terr(train, train)
print 'Error on training set:', err

# check that the result is highly significant since we know that the
# data has signal
print 'Corresponding p-value: ',  terr.ca.null_prob
