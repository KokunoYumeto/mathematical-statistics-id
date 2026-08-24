#!/usr/bin/env python3
"""Exact structural, mathematical, link, locale, and privacy QA for unit 1."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any
from urllib.parse import unquote, urldefrag, urlparse

sys.dont_write_bytecode = True
import build_first_unit as build_pipeline  # noqa: E402
from bs4 import BeautifulSoup, Comment  # noqa: E402
from bs4.element import Tag  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "authority" / "upstream"
TARGET = ROOT / "source" / "id-ID"
READER = ROOT / "build" / "html-id"
QA_RECEIPT = ROOT / "build" / "FIRST_UNIT_QA_RECEIPT.json"
TRANSLATION_LEDGER = ROOT / "00_control" / "TRANSLATION_LEDGER.csv"

PAIRS = (
    PurePosixPath("random/sample/index.html"),
    PurePosixPath("random/sample/Introduction.html"),
    PurePosixPath("random/sample/Mean.html"),
    PurePosixPath("random/sample/LLN.html"),
    PurePosixPath("random/sample/CLT.html"),
    PurePosixPath("random/sample/Variance.html"),
    PurePosixPath("random/sample/OrderStatistics.html"),
    PurePosixPath("random/sample/Covariance.html"),
    PurePosixPath("random/sample/Normal.html"),
    PurePosixPath("random/point/index.html"),
    PurePosixPath("random/point/Estimators.html"),
    PurePosixPath("random/point/Moments.html"),
    PurePosixPath("random/point/Likelihood.html"),
    PurePosixPath("random/point/Bayes.html"),
    PurePosixPath("random/point/Unbiased.html"),
    PurePosixPath("random/point/Sufficient.html"),
    PurePosixPath("random/interval/index.html"),
    PurePosixPath("random/interval/Introduction.html"),
    PurePosixPath("random/interval/Normal.html"),
    PurePosixPath("random/interval/Bernoulli.html"),
    PurePosixPath("random/interval/BivariateNormal.html"),
    PurePosixPath("random/interval/Bayes.html"),
    PurePosixPath("random/hypothesis/index.html"),
    PurePosixPath("random/hypothesis/Introduction.html"),
    PurePosixPath("random/hypothesis/Normal.html"),
    PurePosixPath("random/hypothesis/Bernoulli.html"),
    PurePosixPath("random/hypothesis/BivariateNormal.html"),
    PurePosixPath("random/hypothesis/Likelihood.html"),
    PurePosixPath("random/hypothesis/ChiSquare.html"),
)

LEGACY_PAIRS = PAIRS[:16]

# Exact current source/target invariants, in translation-ledger order.  The
# tuple fields are: source elements, target core elements, protected TeX spans,
# canonical target-TeX SHA-256, raw align environments, target raw-align
# SHA-256, script/style blocks, units, disclosures, IDs, and stable page ID.
# These values consolidate the page-localizer and the interval/hypothesis batch
# gates; they are deliberately page-specific rather than tolerance ranges.
PAGE_EXPECTATION_ROWS = (
    ("random/sample/index.html", 163, 163, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 1, 0, 0, 6, "o006.random.sample.index.chapter"),
    ("random/sample/Introduction.html", 390, 390, 101, "c7b6e0bd00a95ec6159b230e2a81adcd62baff908ffd3dc52bc0e92649580812", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 22, 16, 35, "o006.random.sample.introduction.page"),
    ("random/sample/Mean.html", 585, 585, 365, "ba9d56c27c1949f3946b47dd6308f6090516863816a573239370a46b9b113c5f", 1, "71de94ae3fc973c1b7b9297c849c9fed2b8324b560b21c0475e9282f83b92b16", 3, 26, 23, 43, "o006.random.sample.mean.page"),
    ("random/sample/LLN.html", 305, 305, 268, "a0ccd2909e5d58b5c23b742bc81263a68e313d983d2c4b58f3de1f6ddb445ee0", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 21, 13, 33, "o006.random.sample.lln.page"),
    ("random/sample/CLT.html", 424, 424, 394, "170e841bdb8020c4193647ed8a3c1ccbaaa625c9d7439a265cf9f8888b25cbda", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 38, 21, 56, "o006.random.sample.clt.page"),
    ("random/sample/Variance.html", 827, 827, 583, "de4a6d757cb570a941980fc9b53e5b1eed5d5d39d9e6ac7448ba2e02a3ef818c", 3, "95f2ad70d5ac4586f8cadc7775b7b92a3e4f72460614446e31a53ece2c4cee4d", 3, 47, 39, 64, "o006.random.sample.variance.page"),
    ("random/sample/OrderStatistics.html", 846, 846, 569, "5c3a345f2184152695b3c5bd19bb9a5e93cff8df226a755ae250bb314b112410", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 4, 51, 34, 73, "o006.random.sample.order-statistics.page"),
    ("random/sample/Covariance.html", 906, 906, 795, "8c4e79634f13147b7d3c0708c63bf66da553eb0a16155d983aa56ad7120c6cdf", 7, "dfaad8f1847e2b1f61c8c1915e802f55a5e054d7e619991c6aa2a0d9e3f8d0d0", 3, 58, 34, 80, "o006.random.sample.covariance.page"),
    ("random/sample/Normal.html", 380, 380, 380, "6fc19f93b209bb46654c85b0cfd1798db1273925a7254dc0b6e80deae079fd85", 1, "6079eb3817a489bd32ae3cb11d91e01989f4ed18eacacb6642cb70a23233b5e1", 3, 29, 21, 44, "o006.random.sample.normal.page"),
    ("random/point/index.html", 155, 155, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 1, 0, 0, 6, "o006.random.point.index.chapter"),
    ("random/point/Estimators.html", 380, 381, 432, "247b47730d121187a4bdbb62d38e2a6df891aadf394f703c9aaef407e45f68da", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 33, 15, 51, "o006.random.point.estimators.page"),
    ("random/point/Moments.html", 440, 440, 649, "9173795c2db4708441d6e36ab9a9b36987a1fb243677c147873d55c42f52a48b", 3, "02425a791c39bcff22d4f583170dd19afc20b5afa0e6e30f3596cf506de5625e", 3, 37, 29, 54, "o006.random.point.moments.page"),
    ("random/point/Likelihood.html", 397, 397, 589, "64e98b85be0925d2fcb4103f514aedac490a49a97f09ea3b41ccb80ad8ef6f45", 3, "3014fc96a21960100677941262c3d752abf7d4132233804df95fe2be5da09a19", 3, 35, 22, 53, "o006.random.point.likelihood.page"),
    ("random/point/Bayes.html", 352, 352, 625, "d2d7074b8d3783651f7ebe02ec9a2123a4bdc1999e2315ff32223869e42c07fc", 8, "887c88f146d79d6aa70fdb8fbc744be2ff8daeb329d5aa027c8e18d4ff211f48", 3, 31, 23, 46, "o006.random.point.bayes.page"),
    ("random/point/Unbiased.html", 306, 306, 243, "822206569e31764bfe5223e3642cf1e3629406315619f6fb18e38309e9eb13bd", 4, "2b92e88ed22485f171fd5f31edc804b68bd7b2d44e289cbd36d174d8778b0c95", 3, 38, 10, 52, "o006.random.point.unbiased.page"),
    ("random/point/Sufficient.html", 436, 436, 804, "3e2547e06ef1e9e70118d0db39a1b8592300a635305fee861537749c0d5a41d1", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 39, 26, 51, "o006.random.point.sufficient.page"),
    ("random/interval/index.html", 148, 148, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 1, 0, 0, 6, "o006.random.interval.index.chapter"),
    ("random/interval/Introduction.html", 249, 249, 290, "0f77ffe887d59ab1c4831646b163986ac78621f37ff56c2b767343397f1bcec6", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 21, 7, 31, "o006.random.interval.introduction.page"),
    ("random/interval/Normal.html", 401, 401, 380, "691ec5c887a19a0daef3ef67cc936ea84323cc48d14046c21f6b2442c39417ff", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 35, 19, 54, "o006.random.interval.normal.page"),
    ("random/interval/Bernoulli.html", 285, 285, 238, "9a1c37f8691cc4d87f2befd6a666bd0e66df6b33d198b30cbb431df659f1b715", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 24, 16, 37, "o006.random.interval.bernoulli.page"),
    ("random/interval/BivariateNormal.html", 303, 304, 267, "bb0910b4a1e51a1fe7471edd76783af784f3913852140b1315fd5385d5e6de55", 1, "2fb99b9c40a57d6f653b0ed2cc1ac4557a9c69e930fd5c30c755a6221c4337da", 3, 21, 12, 30, "o006.random.interval.bivariate-normal.page"),
    ("random/interval/Bayes.html", 206, 206, 281, "63d44d0f15053c6e9ab1930f53e5d8ae24a87fd8498e531000a79b894f213675", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 9, 5, 20, "o006.random.interval.bayes.page"),
    ("random/hypothesis/index.html", 155, 155, 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 1, 0, 0, 6, "o006.random.hypothesis.index.chapter"),
    ("random/hypothesis/Introduction.html", 219, 219, 213, "e6ae38470e6886719657b39908e5fd8bec398d8db7ce7440ed745a94353f9907", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 12, 1, 24, "o006.random.hypothesis.introduction.page"),
    ("random/hypothesis/Normal.html", 463, 463, 459, "53bca63a192ef1062b1948308577c2d79b7454819054929bcd26f001d8032688", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 45, 20, 55, "o006.random.hypothesis.normal.page"),
    ("random/hypothesis/Bernoulli.html", 267, 267, 233, "5784e57fccbbdaa8447a1f67be007685e14d1f3f5cb001de68435c46e260ad1b", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 24, 13, 36, "o006.random.hypothesis.bernoulli.page"),
    ("random/hypothesis/BivariateNormal.html", 255, 255, 300, "5c3b6f19a2d1c5fd8866c925f27e15053e3c32228952af99196ede14760bf946", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", 3, 17, 13, 25, "o006.random.hypothesis.bivariate-normal.page"),
    ("random/hypothesis/Likelihood.html", 212, 212, 252, "f96db6784b9e51abfdb0bd0e30fac6e44fa5ba7c20a0bbff7654758ec01806b8", 1, "5a1f331c5fce1ac18831a306d26cabff5b9b7c14ec82f879c29ab37222522c7b", 3, 18, 7, 29, "o006.random.hypothesis.likelihood.page"),
    ("random/hypothesis/ChiSquare.html", 417, 417, 433, "436124f6fc9324c8d541f847fbe9cdcd3550c93c021947b795738d47b46b6f10", 2, "52c07b796a2dbf7595bd1670df92ec81cec3d2b27b1cff17c6501b15d65f5876", 3, 29, 12, 48, "o006.random.hypothesis.chi-square.page"),
)

PAGE_EXPECTATIONS = {
    PurePosixPath(row[0]): {
        "source_elements": row[1],
        "target_elements": row[2],
        "math_spans": row[3],
        "target_math_sha256": row[4],
        "raw_math_environments": row[5],
        "target_raw_math_sha256": row[6],
        "raw_script_style_blocks": row[7],
        "units": row[8],
        "details": row[9],
        "ids": row[10],
        "page_id": row[11],
    }
    for row in PAGE_EXPECTATION_ROWS
}

# The sole admitted topology repair restores the paragraph opener missing from
# the frozen ordinal-21 authority.  The target element index is one-based.
TARGET_ELEMENT_INSERTIONS = {
    PurePosixPath("random/point/Estimators.html"): (54, "summary", {}),
    PurePosixPath("random/interval/BivariateNormal.html"): (56, "p", {}),
}

ELEMENT_ATTRIBUTE_DELTAS = {
    (PurePosixPath("random/interval/Introduction.html"), 110, "src"): (
        "Tails.png",
        "Tails-id.svg",
    ),
}

# Exact fingerprints of every source/target href pair (including unchanged
# local core links) and of the changed subset.  These are generated from paired
# element streams after applying only TARGET_ELEMENT_INSERTIONS.  They keep the
# href surface exact without reintroducing stale pre-interval publication
# targets into the historical 1-16 allowlist.
HREF_PAIR_EXPECTATIONS = {
    PurePosixPath("random/sample/index.html"): (68, "5b1f09760f287b56679ed4a971ac42dda6a4773de68d8c1d79dda7e05edbaec7", 50, "02921dbddbded17af467f7d00895a15552fe7d293341b29dcdc7d70af3ac2917"),
    PurePosixPath("random/sample/Introduction.html"): (72, "daac2825a6cdb51b106116abc5f9ce71333132e866080cc18f7f9b04c849ec34", 54, "77ac52aa0fd3913e928937f9c95b40c9582b71ff42a2df82a870a9a5042117d0"),
    PurePosixPath("random/sample/Mean.html"): (47, "cf0e6abeccc882fcc3246c71548cb376306440d69b028bfee874f094fca5b8b9", 21, "ce7f4fa37b6671aa27702a143944371739287aec45b5d691d4e5930f6664932e"),
    PurePosixPath("random/sample/LLN.html"): (67, "c156f78d77e5ab3226aa58082d7f4ea4eaa4909c73806481ac8c525c7a6a5f78", 36, "66d1074d7a5447709582903afe813e9e2dc46dfc3a67eb8b1b4c176c32a0c496"),
    PurePosixPath("random/sample/CLT.html"): (95, "fa2e4ac1c3c6922bfeea5ecc5467361cd1c6c6154083166d8fd6240db547249d", 67, "df90a6332cd1ca2bde1d2c22a5d52a4da650c31832fbecdcd6ff19327dfb4be6"),
    PurePosixPath("random/sample/Variance.html"): (65, "f100b4f613538e6de596d96176810417f5c3fb9afb43e90960256e0df568d6f9", 32, "ff1fcc5696a0689b4b463ea9e410199023feca547ee386419f13c915f27d962c"),
    PurePosixPath("random/sample/OrderStatistics.html"): (82, "53886b1a3d0ca59c1f2ec4409d365ea68d4b8447901b8075f48e02032abd73d8", 45, "e63f6a81c3e66b5b46c270ad66e0ace9fbcd70de9106a00b140d36503a7060df"),
    PurePosixPath("random/sample/Covariance.html"): (80, "6c5285878aa3538ed6d0eb17e6b456d2ff28cd2f18b63e5dc2bc555ed016e850", 30, "75ddd2da266cd68cf79ef5e2e4f8ce0034f39da6589decb193d0fd018c0493c7"),
    PurePosixPath("random/sample/Normal.html"): (90, "c7724df1d311e7ed6090a1f242968b8a0bb70e9cee3a146abec021fb44bd2935", 23, "0314602d3cb9976330f54ca6d8df09a2b8a7eda7a9a5ef01e7dd82d4d60778be"),
    PurePosixPath("random/point/index.html"): (65, "a73b844b3b455fe6942ef0dacff1eb90a573902082095fcfbb47fea5e9d5a7fc", 48, "490b7fa909858211a43f250ba504d879517a2c91b70620956b3513edd74d7ea2"),
    PurePosixPath("random/point/Estimators.html"): (60, "3f661ea9fcea80b311a18677063dddac5a4d6fa0800c34e36a44ba555a76c173", 31, "5753207f773052bf3c788adb3147143a601a0fb81dc5c36a5591dc8b44aec9c8"),
    PurePosixPath("random/point/Moments.html"): (72, "32bafb906813efdd46ac72a273dc2b0882d584f743a886162794e43c8b73f28f", 40, "304a2f4b40c2e63aabd8792ce3a235e383e87426cd738e4e2d76d1b16b763a87"),
    PurePosixPath("random/point/Likelihood.html"): (69, "758517c8e5c166e42bd6a8e2e17fa7d1fc1230f51a7eab174843b5e799d5a71f", 34, "ed96be9f001c438160185bcea8abc6077d0ef216c2dbfface36432b9edad775d"),
    PurePosixPath("random/point/Bayes.html"): (72, "526573572f0c60ae55f84a8c59737811ebd588ccc7babfe9cbfe6dfcd2ce49d3", 36, "12a9c855d89d1f62565bd67fc17b4523adfd9ad5b10e88c825b6dca99ec78cda"),
    PurePosixPath("random/point/Unbiased.html"): (89, "0f019410f5fffb23519724bc88a13bf1152cc7a7a501a4647db00767dd20916a", 34, "51c038883ad010a7007d94400706d0014ae783ee860fca5a4dfec554f1a4deec"),
    PurePosixPath("random/point/Sufficient.html"): (118, "be28ab668025060cad83d5bc00ede6daaa2655e66f56043bb6959be092ffa9c3", 43, "27b555727f6306d8356a33ab2af323a60307295daa0ee04d2f37bbb71f6e0ef3"),
    PurePosixPath("random/interval/index.html"): (62, "fbc7e4d309f196efc1e95cb5e6f1aad510d04b6344c5289af4b2c5dfbcfc423c", 46, "d0a9221a807d7e59f6496fadb6b9455072b228c3e856f78ce9c87a31aa5bc5ae"),
    PurePosixPath("random/interval/Introduction.html"): (41, "61c9affaabba43efca2d69b0f262f960bc37ecc9a2974722e989be6730b7bf50", 18, "9dfdbaee68bb15226e6790a0b009f5f16e5019b927c2e2d3ebb9cb5f5a628cb0"),
    PurePosixPath("random/interval/Normal.html"): (51, "223f4cb057ed117f2eac3ccc13fafc2a77af92c1962198483146ad11997bcb04", 25, "3eec47fe9ef881cab95c1c9a90bd7fd48ad422c1972f9a53402ac642572e3aef"),
    PurePosixPath("random/interval/Bernoulli.html"): (52, "a50e7d013bcf86992e92a429c5cc6b999552434445066646f88e06ea63c3abeb", 21, "12c199235344116d49ffdffa037ca46ac988aecf7190cc3578667edc22e9662d"),
    PurePosixPath("random/interval/BivariateNormal.html"): (48, "c61d01daa9df7ceb5bd71d99a96ebfce8fba6bd5675d2a14fd566aa38d765a85", 19, "7fc04ef27ac95fca8afda90b3239f3534f4b948e395bf34d8e0a43e7dd4a6b8d"),
    PurePosixPath("random/interval/Bayes.html"): (51, "3c4e48efc1d3b208ff06664b49a7a3c1468b65d59b9ceaefaad9fec2e3bdac3d", 28, "aef6cefb39fd488f834c291080b8d0db47e2a4f9e84b303b2dafa97dcca4cd23"),
    PurePosixPath("random/hypothesis/index.html"): (66, "5519bebd113926204496bb189682dd422f185bcfccdad9527b93a70da0ca0f34", 50, "1408f186bac2919977f5c83f1069d407090b8a15bdd7cd0fa35b22a509940a34"),
    PurePosixPath("random/hypothesis/Introduction.html"): (28, "fd445b03944799b4db6692d6bd4fa048d5e1d98963c6ea750c09ce6f45794040", 10, "cebd4cecead0c736b8281541f5f0c69262cb1aa4d40bf1798070b74e6c05b11a"),
    PurePosixPath("random/hypothesis/Normal.html"): (89, "9799355c8d5d8b3122909519ced347902324ce379340ffae828b56360ff86586", 40, "cfb5e0e91c405630495e1789396ffeb5760099bf9890f2b8c1b4f9a6f4eb383a"),
    PurePosixPath("random/hypothesis/Bernoulli.html"): (52, "2e0f7771ee656d9a8dc0b8ada22fc8d721e0c54cab4a53aa9501165dd73582c7", 29, "45246e2a81728d0cfb0b87710e3d87994c4aac735b15f11a22b4c97ea3a9f040"),
    PurePosixPath("random/hypothesis/BivariateNormal.html"): (46, "6b48bd7755ecdd891be2e8e63ecf046b063e5816267cc48cc6ce69840f36e59d", 18, "9da535001eb65433ca6136330914d79705d8908e721fbebbb3beca50d88555e4"),
    PurePosixPath("random/hypothesis/Likelihood.html"): (39, "fb293c08ef6259adc478084af2658dec1407b42b610598a7dafed41181af1da6", 20, "2d5e3a8310964395a399d9ab94d11fafab96d6e424acb3bae42a8060a819c3af"),
    PurePosixPath("random/hypothesis/ChiSquare.html"): (64, "94a30337f02974e83fe1272d9ee7fa126a9eda65f31e29927addae7fb2e39266", 28, "8e25190efa4120faa32f52b84cb4f87b2f61a5291012d25f1f49ec90f0c1143f"),
}

# This is an exact page/original-href allowlist. There is deliberately no URL
# rewriting rule, suffix heuristic, or substring replacement in the verifier.
HREF_DELTA_ALLOWLIST: dict[PurePosixPath, dict[str, str]] = {
    PurePosixPath("random/sample/index.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../special/index.html": "https://www.randomservices.org/random/special/index.html",
        "../foundations/index.html": "https://www.randomservices.org/random/foundations/index.html",
        "../prob/index.html": "https://www.randomservices.org/random/prob/index.html",
        "../dist/index.html": "https://www.randomservices.org/random/dist/index.html",
        "../expect/index.html": "https://www.randomservices.org/random/expect/index.html",
        "../buffon/index.html": "https://www.randomservices.org/random/buffon/index.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "../games/index.html": "https://www.randomservices.org/random/games/index.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../renewal/index.html": "https://www.randomservices.org/random/renewal/index.html",
        "../markov/index.html": "https://www.randomservices.org/random/markov/index.html",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../brown/index.html": "https://www.randomservices.org/random/brown/index.html",
        "JavaScript:openAncillary('../apps/Histogram.html')": "https://www.randomservices.org/random/apps/Histogram.html",
        "JavaScript:openAncillary('../apps/ErrorFunction.html')": "https://www.randomservices.org/random/apps/ErrorFunction.html",
        "JavaScript:openAncillary('../apps/Dice.html')": "https://www.randomservices.org/random/apps/Dice.html",
        "JavaScript:openAncillary('../apps/SampleMean.html')": "https://www.randomservices.org/random/apps/SampleMean.html",
        "JavaScript:openAncillary('../apps/OrderStatistic.html')": "https://www.randomservices.org/random/apps/OrderStatistic.html",
        "JavaScript:openAncillary('../apps/ProbabilityPlot.html')": "https://www.randomservices.org/random/apps/ProbabilityPlot.html",
        "JavaScript:openAncillary('../apps/Scatterplot.html')": "https://www.randomservices.org/random/apps/Scatterplot.html",
        "JavaScript:openAncillary('../biographies/Clemens.html')": "https://www.randomservices.org/random/biographies/Clemens.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
        "http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt": "https://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt",
        "http://www.google.com/search?q=Statistical+Inference+Casella+Berger": "https://www.google.com/search?q=Statistical+Inference+Casella+Berger",
        "http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves": "https://www.google.com/search?q=Statistics,Freedman,Pisani,Purves",
        "http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx": "https://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx",
        "http://www.google.com/search?q=Elementary+Statistics,Triola": "https://www.google.com/search?q=Elementary+Statistics,Triola",
        "http://www.google.com/search?q=Introductory+Statistics,Weiss": "https://www.google.com/search?q=Introductory+Statistics,Weiss",
        "http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html": "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
    },
    PurePosixPath("random/sample/Introduction.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Polio.html')": "https://www.randomservices.org/random/data/Polio.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../data/Snow.html')": "https://www.randomservices.org/random/data/Snow.html",
        "JavaScript:openAncillary('../data/SAT.html')": "https://www.randomservices.org/random/data/SAT.html",
        "../dist/discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../foundations/Equivalence.html": "https://www.randomservices.org/random/foundations/Equivalence.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Events.html": "https://www.randomservices.org/random/prob/Events.html",
        "JavaScript:openAncillary('../data/Berkeley.html')": "https://www.randomservices.org/random/data/Berkeley.html",
        "JavaScript:openAncillary('../data/LiteraryDigest.html')": "https://www.randomservices.org/random/data/LiteraryDigest.html",
        "JavaScript:openAncillary('../data/1948Election.html')": "https://www.randomservices.org/random/data/Election1948.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Draft.html')": "https://www.randomservices.org/random/data/Draft.html",
        "../buffon/Buffon.html": "https://www.randomservices.org/random/buffon/Buffon.html",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "../poisson/Introduction.html": "https://www.randomservices.org/random/poisson/Introduction.html",
        "../special/index.html": "https://www.randomservices.org/random/special/index.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "../special/Weibull.html": "https://www.randomservices.org/random/special/Weibull.html",
        "../urn/OrderStatistics.html": "https://www.randomservices.org/random/urn/OrderStatistics.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/Mean.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../dist/Discrete.html#uni": "https://www.randomservices.org/random/dist/Discrete.html#uni",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../dist/CDF.html": "https://www.randomservices.org/random/dist/CDF.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "JavaScript:openAncillary('../apps/Histogram.html')": "https://www.randomservices.org/random/apps/Histogram.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/LLN.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../expect/Spaces.html#con": "https://www.randomservices.org/random/expect/Spaces.html#con",
        "../prob/Convergence.html#lim2": "https://www.randomservices.org/random/prob/Convergence.html#lim2",
        "../expect/Variance.html#chb": "https://www.randomservices.org/random/expect/Variance.html#chb",
        "../prob/Convergence.html#lim1": "https://www.randomservices.org/random/prob/Convergence.html#lim1",
        "../prob/Convergence.html": "https://www.randomservices.org/random/prob/Convergence.html",
        "../martingales/Backwards.html#lln": "https://www.randomservices.org/random/martingales/Backwards.html#lln",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../dist/CDF.html": "https://www.randomservices.org/random/dist/CDF.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "JavaScript:openAncillary('../apps/Dice.html')": "https://www.randomservices.org/random/apps/Dice.html",
        "JavaScript:openAncillary('../apps/BuffonCoin.html')": "https://www.randomservices.org/random/apps/BuffonCoin.html",
        "JavaScript:openAncillary('../apps/Bertrand.html')": "https://www.randomservices.org/random/apps/Bertrand.html",
        "JavaScript:openAncillary('../apps/BinomialCoin.html')": "https://www.randomservices.org/random/apps/BinomialCoin.html",
        "JavaScript:openAncillary('../apps/Match.html')": "https://www.randomservices.org/random/apps/Match.html",
        "JavaScript:openAncillary('../apps/Poker.html')": "https://www.randomservices.org/random/apps/Poker.html",
        "JavaScript:openAncillary('../apps/Gamma.html')": "https://www.randomservices.org/random/apps/Gamma.html",
        "JavaScript:openAncillary('../apps/SpecialSimulator.html')": "https://www.randomservices.org/random/apps/SpecialSimulator.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/CLT.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Independence.html": "https://www.randomservices.org/random/prob/Independence.html",
        "../prob/Events.html": "https://www.randomservices.org/random/prob/Events.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../bernoulli/NegativeBinomial.html": "https://www.randomservices.org/random/bernoulli/NegativeBinomial.html",
        "../poisson/Gamma.html": "https://www.randomservices.org/random/poisson/Gamma.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../renewal/Introduction.html": "https://www.randomservices.org/random/renewal/Introduction.html",
        "../renewal/index.html": "https://www.randomservices.org/random/renewal/index.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "../brown/Standard.html": "https://www.randomservices.org/random/brown/Standard.html",
        "../expect/Covariance.html": "https://www.randomservices.org/random/expect/Covariance.html",
        "../expect/Generating.html#mgf": "https://www.randomservices.org/random/expect/Generating.html#mgf",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "../dist/Transformations.html#sum": "https://www.randomservices.org/random/dist/Transformations.html#sum",
        "../dist/Transformations.html": "https://www.randomservices.org/random/dist/Transformations.html",
        "../dist/Convergence.html": "https://www.randomservices.org/random/dist/Convergence.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "JavaScript:openAncillary('../biographies/DeMoivre.html')": "https://www.randomservices.org/random/biographies/DeMoivre.html",
        "JavaScript:openAncillary('../biographies/Polya.html')": "https://www.randomservices.org/random/biographies/Polya.html",
        "../dist/CDF.html": "https://www.randomservices.org/random/dist/CDF.html",
        "JavaScript:openAncillary('../biographies/Taylor.html')": "https://www.randomservices.org/random/biographies/Taylor.html",
        "../special/IrwinHall.html": "https://www.randomservices.org/random/special/IrwinHall.html",
        "JavaScript:openAncillary('../apps/SpecialSimulator.html')": "https://www.randomservices.org/random/apps/SpecialSimulator.html",
        "JavaScript:openAncillary('../biographies/Pareto.html')": "https://www.randomservices.org/random/biographies/Pareto.html",
        "JavaScript:openAncillary('../apps/Dice.html')": "https://www.randomservices.org/random/apps/Dice.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "JavaScript:openAncillary('../biographies/Erlang.html')": "https://www.randomservices.org/random/biographies/Erlang.html",
        "../special/ChiSquare.html": "https://www.randomservices.org/random/special/ChiSquare.html",
        "JavaScript:openAncillary('../biographies/Bernoulli.html')": "https://www.randomservices.org/random/biographies/Bernoulli.html",
        "JavaScript:openAncillary('../apps/BinomialTimeline.html')": "https://www.randomservices.org/random/apps/BinomialTimeline.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "JavaScript:openAncillary('../apps/Poisson.html')": "https://www.randomservices.org/random/apps/Poisson.html",
        "../bernoulli/Geometric.html": "https://www.randomservices.org/random/bernoulli/Geometric.html",
        "JavaScript:openAncillary('../apps/NegativeBinomial.html')": "https://www.randomservices.org/random/apps/NegativeBinomial.html",
        "../expect/Conditional.html": "https://www.randomservices.org/random/expect/Conditional.html",
        "../prob/Stop.html": "https://www.randomservices.org/random/prob/Stop.html",
        "../foundations/Measure.html": "https://www.randomservices.org/random/foundations/Measure.html",
        "JavaScript:openAncillary('../biographies/Wald.html')": "https://www.randomservices.org/random/biographies/Wald.html",
        "../martingales/Stop.html#wld": "https://www.randomservices.org/random/martingales/Stop.html#wld",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../dist/Continuous.html#uni": "https://www.randomservices.org/random/dist/Continuous.html#uni",
        "../poisson/Exponential.html": "https://www.randomservices.org/random/poisson/Exponential.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/Variance.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../dist/Discrete.html#uni": "https://www.randomservices.org/random/dist/Discrete.html#uni",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../expect/Properties2.html#jen": "https://www.randomservices.org/random/expect/Properties2.html#jen",
        "JavaScript:openAncillary('../apps/ErrorFunction.html')": "https://www.randomservices.org/random/apps/ErrorFunction.html",
        "JavaScript:openAncillary('../apps/BinomialCoin.html')": "https://www.randomservices.org/random/apps/BinomialCoin.html",
        "JavaScript:openAncillary('../apps/Match.html')": "https://www.randomservices.org/random/apps/Match.html",
        "JavaScript:openAncillary('../apps/Gamma.html')": "https://www.randomservices.org/random/apps/Gamma.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../poisson/Exponential.html": "https://www.randomservices.org/random/poisson/Exponential.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/OrderStatistics.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../dist/CDF.html": "https://www.randomservices.org/random/dist/CDF.html",
        "../dist/Discrete.html#uni": "https://www.randomservices.org/random/dist/Discrete.html#uni",
        "../dist/CDF.html#qnt": "https://www.randomservices.org/random/dist/CDF.html#qnt",
        "../expect/Properties2.html#jen": "https://www.randomservices.org/random/expect/Properties2.html#jen",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Independence.html": "https://www.randomservices.org/random/prob/Independence.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "../dist/Transformations.html#cov": "https://www.randomservices.org/random/dist/Transformations.html#cov",
        "../special/LocationScale.html": "https://www.randomservices.org/random/special/LocationScale.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../poisson/Exponential.html": "https://www.randomservices.org/random/poisson/Exponential.html",
        "../dist/Continuous.html#uni": "https://www.randomservices.org/random/dist/Continuous.html#uni",
        "JavaScript:openAncillary('../apps/Histogram.html')": "https://www.randomservices.org/random/apps/Histogram.html",
        "JavaScript:openAncillary('../apps/ErrorFunction.html')": "https://www.randomservices.org/random/apps/ErrorFunction.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "JavaScript:openAncillary('../apps/OrderStatistic.html')": "https://www.randomservices.org/random/apps/OrderStatistic.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "JavaScript:openAncillary('../apps/Dice.html')": "https://www.randomservices.org/random/apps/Dice.html",
        "JavaScript:openAncillary('../apps/ProbabilityPlot.html')": "https://www.randomservices.org/random/apps/ProbabilityPlot.html",
        "JavaScript:openAncillary('../data/Fisher.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/Covariance.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../dist/Discrete.html#uni": "https://www.randomservices.org/random/dist/Discrete.html#uni",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../expect/Covariance.html": "https://www.randomservices.org/random/expect/Covariance.html",
        "JavaScript:openAncillary('../data/Challenger.html')": "https://www.randomservices.org/random/data/Challenger.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Independence.html": "https://www.randomservices.org/random/prob/Independence.html",
        "../expect/Covariance.html#blp": "https://www.randomservices.org/random/expect/Covariance.html#blp",
        "JavaScript:openAncillary('../apps/Scatterplot.html')": "https://www.randomservices.org/random/apps/Scatterplot.html",
        "JavaScript:openAncillary('../apps/BivariateUniform.html')": "https://www.randomservices.org/random/apps/BivariateUniform.html",
        "JavaScript:openAncillary('../apps/BivariateNormal.html')": "https://www.randomservices.org/random/apps/BivariateNormal.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../data/Iris.html')": "https://www.randomservices.org/random/data/Iris.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/SAT.html')": "https://www.randomservices.org/random/data/SAT.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/sample/Normal.html"): {
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Skew.html#skw": "https://www.randomservices.org/random/expect/Skew.html#skw",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Independence.html": "https://www.randomservices.org/random/prob/Independence.html",
        "../special/ChiSquare.html": "https://www.randomservices.org/random/special/ChiSquare.html",
        "../special/Fisher.html": "https://www.randomservices.org/random/special/Fisher.html",
        "../special/MultiNormal.html": "https://www.randomservices.org/random/special/MultiNormal.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Student.html": "https://www.randomservices.org/random/special/Student.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../apps/SpecialSimulator.html')": "https://www.randomservices.org/random/apps/SpecialSimulator.html",
        "JavaScript:openAncillary('../biographies/Fisher.html')": "https://www.randomservices.org/random/biographies/Fisher.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
    },
    PurePosixPath("random/point/index.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../foundations/index.html": "https://www.randomservices.org/random/foundations/index.html",
        "../prob/index.html": "https://www.randomservices.org/random/prob/index.html",
        "../dist/index.html": "https://www.randomservices.org/random/dist/index.html",
        "../expect/index.html": "https://www.randomservices.org/random/expect/index.html",
        "../special/index.html": "https://www.randomservices.org/random/special/index.html",
        "../buffon/index.html": "https://www.randomservices.org/random/buffon/index.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "../games/index.html": "https://www.randomservices.org/random/games/index.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../renewal/index.html": "https://www.randomservices.org/random/renewal/index.html",
        "../markov/index.html": "https://www.randomservices.org/random/markov/index.html",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../brown/index.html": "https://www.randomservices.org/random/brown/index.html",
        "JavaScript:openAncillary('../apps/NormalEstimate.html')": "https://www.randomservices.org/random/apps/NormalEstimate.html",
        "JavaScript:openAncillary('../apps/UniformEstimate.html')": "https://www.randomservices.org/random/apps/UniformEstimate.html",
        "JavaScript:openAncillary('../apps/GammaEstimate.html')": "https://www.randomservices.org/random/apps/GammaEstimate.html",
        "JavaScript:openAncillary('../apps/BetaEstimate.html')": "https://www.randomservices.org/random/apps/BetaEstimate.html",
        "JavaScript:openAncillary('../apps/ParetoEstimate.html')": "https://www.randomservices.org/random/apps/ParetoEstimate.html",
        "JavaScript:openAncillary('../apps/BetaCoin.html')": "https://www.randomservices.org/random/apps/BetaCoin.html",
        "http://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt": "https://www.google.com/search?q=Introduction+to+Probability+and+Mathematical+Statistics,+Bain,+Engelhardt",
        "http://www.google.com/search?q=Statistical+Inference+Casella+Berger": "https://www.google.com/search?q=Statistical+Inference+Casella+Berger",
        "http://www.google.com/search?q=Statistics,Freedman,Pisani,Purves": "https://www.google.com/search?q=Statistics,Freedman,Pisani,Purves",
        "http://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx": "https://www.google.com/search?q=An+Introduction+to+Mathematical+Statistics,Larsen,Marx",
        "http://www.google.com/search?q=Elementary+Statistics,Triola": "https://www.google.com/search?q=Elementary+Statistics,Triola",
        "http://www.google.com/search?q=Introductory+Statistics,Weiss": "https://www.google.com/search?q=Introductory+Statistics,Weiss",
        "http://mathworld.wolfram.com/topics/ProbabilityandStatistics.html": "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        "JavaScript:openAncillary('../biographies/Tukey.html')": "https://www.randomservices.org/random/biographies/Tukey.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/point/Estimators.html"): {
        "../expect/Covariance.html#blp": "https://www.randomservices.org/random/expect/Covariance.html#blp",
        "../expect/Properties2.html#mar": "https://www.randomservices.org/random/expect/Properties2.html#mar",
        "../expect/Skew.html#kur": "https://www.randomservices.org/random/expect/Skew.html#kur",
        "../expect/Spaces.html": "https://www.randomservices.org/random/expect/Spaces.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../foundations/Measurable.html": "https://www.randomservices.org/random/foundations/Measurable.html",
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../prob/Convergence.html": "https://www.randomservices.org/random/prob/Convergence.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Probability2.html": "https://www.randomservices.org/random/prob/Probability2.html",
        "JavaScript:openAncillary('../apps/ExponentialExperiment.html')": "https://www.randomservices.org/random/apps/ExponentialExperiment.html",
        "JavaScript:openAncillary('../apps/Match.html')": "https://www.randomservices.org/random/apps/Match.html",
        "JavaScript:openAncillary('../apps/MeanEstimate.html')": "https://www.randomservices.org/random/apps/MeanEstimate.html",
        "JavaScript:openAncillary('../apps/NormalEstimate.html')": "https://www.randomservices.org/random/apps/NormalEstimate.html",
        "JavaScript:openAncillary('../apps/Poisson.html')": "https://www.randomservices.org/random/apps/Poisson.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
        "JavaScript:openAncillary('../data/Alpha.html')": "https://www.randomservices.org/random/data/Alpha.html",
        "JavaScript:openAncillary('../data/Cavendish.html')": "https://www.randomservices.org/random/data/Cavendish.html",
        "JavaScript:openAncillary('../data/Cicada.html')": "https://www.randomservices.org/random/data/Cicada.html",
        "JavaScript:openAncillary('../data/MM.html')": "https://www.randomservices.org/random/data/MM.html",
        "JavaScript:openAncillary('../data/Michelson.html')": "https://www.randomservices.org/random/data/Michelson.html",
        "JavaScript:openAncillary('../data/Pearson.html')": "https://www.randomservices.org/random/data/Pearson.html",
        "JavaScript:openAncillary('../data/Short.html')": "https://www.randomservices.org/random/data/Short.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
    },
    PurePosixPath("random/point/Moments.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Independence.html": "https://www.randomservices.org/random/prob/Independence.html",
        "../expect/Properties.html#mom": "https://www.randomservices.org/random/expect/Properties.html#mom",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "JavaScript:openAncillary('../apps/NormalEstimate.html')": "https://www.randomservices.org/random/apps/NormalEstimate.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/ChiSquare.html": "https://www.randomservices.org/random/special/ChiSquare.html",
        "../special/ChiSquare.html#chi": "https://www.randomservices.org/random/special/ChiSquare.html#chi",
        "JavaScript:openAncillary('../biographies/Bernoulli.html')": "https://www.randomservices.org/random/biographies/Bernoulli.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../bernoulli/Geometric.html": "https://www.randomservices.org/random/bernoulli/Geometric.html",
        "../bernoulli/NegativeBinomial.html": "https://www.randomservices.org/random/bernoulli/NegativeBinomial.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../poisson/Gamma.html": "https://www.randomservices.org/random/poisson/Gamma.html",
        "JavaScript:openAncillary('../biographies/Erlang.html')": "https://www.randomservices.org/random/biographies/Erlang.html",
        "JavaScript:openAncillary('../apps/GammaEstimate.html')": "https://www.randomservices.org/random/apps/GammaEstimate.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "JavaScript:openAncillary('../apps/BetaEstimate.html')": "https://www.randomservices.org/random/apps/BetaEstimate.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "JavaScript:openAncillary('../biographies/Pareto.html')": "https://www.randomservices.org/random/biographies/Pareto.html",
        "JavaScript:openAncillary('../apps/ParetoEstimate.html')": "https://www.randomservices.org/random/apps/ParetoEstimate.html",
        "../special/UniformContinuous.html": "https://www.randomservices.org/random/special/UniformContinuous.html",
        "../urn/Hypergeometric.html": "https://www.randomservices.org/random/urn/Hypergeometric.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/point/Likelihood.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "../dist/Continuous.html#uni": "https://www.randomservices.org/random/dist/Continuous.html#uni",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../bernoulli/Geometric.html": "https://www.randomservices.org/random/bernoulli/Geometric.html",
        "../bernoulli/NegativeBinomial.html": "https://www.randomservices.org/random/bernoulli/NegativeBinomial.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "../urn/OrderStatistics.html": "https://www.randomservices.org/random/urn/OrderStatistics.html",
        "../urn/Hypergeometric.html": "https://www.randomservices.org/random/urn/Hypergeometric.html",
        "../urn/index.html": "https://www.randomservices.org/random/urn/index.html",
        "JavaScript:openAncillary('../apps/NormalEstimate.html')": "https://www.randomservices.org/random/apps/NormalEstimate.html",
        "JavaScript:openAncillary('../apps/GammaEstimate.html')": "https://www.randomservices.org/random/apps/GammaEstimate.html",
        "JavaScript:openAncillary('../apps/BetaEstimate.html')": "https://www.randomservices.org/random/apps/BetaEstimate.html",
        "JavaScript:openAncillary('../apps/ParetoEstimate.html')": "https://www.randomservices.org/random/apps/ParetoEstimate.html",
        "JavaScript:openAncillary('../apps/UniformEstimate.html')": "https://www.randomservices.org/random/apps/UniformEstimate.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "JavaScript:openAncillary('../biographies/Pareto.html')": "https://www.randomservices.org/random/biographies/Pareto.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
    },
    PurePosixPath("random/point/Bayes.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "../dist/Continuous.html": "https://www.randomservices.org/random/dist/Continuous.html",
        "JavaScript:openAncillary('../biographies/Bayes.html')": "https://www.randomservices.org/random/biographies/Bayes.html",
        "../dist/Conditional.html#bay": "https://www.randomservices.org/random/dist/Conditional.html#bay",
        "../dist/Joint.html": "https://www.randomservices.org/random/dist/Joint.html",
        "../special/Uniform.html": "https://www.randomservices.org/random/special/Uniform.html",
        "../expect/Conditional.html": "https://www.randomservices.org/random/expect/Conditional.html",
        "../martingales/index.html": "https://www.randomservices.org/random/martingales/index.html",
        "../expect/Spaces.html#cen": "https://www.randomservices.org/random/expect/Spaces.html#cen",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../bernoulli/BetaBernoulli.html": "https://www.randomservices.org/random/bernoulli/BetaBernoulli.html",
        "JavaScript:openAncillary('../apps/BetaCoin.html')": "https://www.randomservices.org/random/apps/BetaCoin.html",
        "../bernoulli/Geometric.html": "https://www.randomservices.org/random/bernoulli/Geometric.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "../bernoulli/NegativeBinomial.html": "https://www.randomservices.org/random/bernoulli/NegativeBinomial.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "JavaScript:openAncillary('../biographies/Pareto.html')": "https://www.randomservices.org/random/biographies/Pareto.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/point/Unbiased.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../dist/index.html": "https://www.randomservices.org/random/dist/index.html",
        "../expect/Properties.html": "https://www.randomservices.org/random/expect/Properties.html",
        "../expect/Variance.html": "https://www.randomservices.org/random/expect/Variance.html",
        "../expect/Covariance.html": "https://www.randomservices.org/random/expect/Covariance.html",
        "JavaScript:openAncillary('../biographies/Cramer.html')": "https://www.randomservices.org/random/biographies/Cramer.html",
        "JavaScript:openAncillary('../biographies/Rao.html')": "https://www.randomservices.org/random/biographies/Rao.html",
        "../expect/Covariance.html#blp6": "https://www.randomservices.org/random/expect/Covariance.html#blp6",
        "JavaScript:openAncillary('../biographies/Fisher.html')": "https://www.randomservices.org/random/biographies/Fisher.html",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "JavaScript:openAncillary('../biographies/Bernoulli.html')": "https://www.randomservices.org/random/biographies/Bernoulli.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../special/UniformContinuous.html": "https://www.randomservices.org/random/special/UniformContinuous.html",
        "JavaScript:openAncillary('../biographies/Lagrange.html')": "https://www.randomservices.org/random/biographies/Lagrange.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
    PurePosixPath("random/point/Sufficient.html"): {
        "../index.html": "https://www.randomservices.org/random/index.html",
        "../prob/Experiments.html": "https://www.randomservices.org/random/prob/Experiments.html",
        "../prob/Probability.html": "https://www.randomservices.org/random/prob/Probability.html",
        "../dist/Conditional.html": "https://www.randomservices.org/random/dist/Conditional.html",
        "../dist/Discrete.html": "https://www.randomservices.org/random/dist/Discrete.html",
        "JavaScript:openAncillary('../biographies/Fisher.html')": "https://www.randomservices.org/random/biographies/Fisher.html",
        "JavaScript:openAncillary('../biographies/Neyman.html')": "https://www.randomservices.org/random/biographies/Neyman.html",
        "../expect/Conditional.html": "https://www.randomservices.org/random/expect/Conditional.html",
        "JavaScript:openAncillary('../biographies/Rao.html')": "https://www.randomservices.org/random/biographies/Rao.html",
        "JavaScript:openAncillary('../biographies/Blackwell.html')": "https://www.randomservices.org/random/biographies/Blackwell.html",
        "JavaScript:openAncillary('../biographies/Lehmann.html')": "https://www.randomservices.org/random/biographies/Lehmann.html",
        "JavaScript:openAncillary('../biographies/Scheffe.html')": "https://www.randomservices.org/random/biographies/Scheffe.html",
        "../bernoulli/Introduction.html": "https://www.randomservices.org/random/bernoulli/Introduction.html",
        "../bernoulli/index.html": "https://www.randomservices.org/random/bernoulli/index.html",
        "JavaScript:openAncillary('../biographies/Bernoulli.html')": "https://www.randomservices.org/random/biographies/Bernoulli.html",
        "../bernoulli/Binomial.html": "https://www.randomservices.org/random/bernoulli/Binomial.html",
        "../special/Beta.html": "https://www.randomservices.org/random/special/Beta.html",
        "../poisson/Poisson.html": "https://www.randomservices.org/random/poisson/Poisson.html",
        "JavaScript:openAncillary('../biographies/Poisson.html')": "https://www.randomservices.org/random/biographies/Poisson.html",
        "../poisson/index.html": "https://www.randomservices.org/random/poisson/index.html",
        "../bernoulli/Multinomial.html": "https://www.randomservices.org/random/bernoulli/Multinomial.html",
        "../expect/Generating.html#pgf": "https://www.randomservices.org/random/expect/Generating.html#pgf",
        "../special/Normal.html": "https://www.randomservices.org/random/special/Normal.html",
        "JavaScript:openAncillary('../apps/NormalEstimate.html')": "https://www.randomservices.org/random/apps/NormalEstimate.html",
        "../special/ChiSquare.html": "https://www.randomservices.org/random/special/ChiSquare.html",
        "../special/Gamma.html": "https://www.randomservices.org/random/special/Gamma.html",
        "JavaScript:openAncillary('../apps/GammaEstimate.html')": "https://www.randomservices.org/random/apps/GammaEstimate.html",
        "JavaScript:openAncillary('../apps/BetaEstimate.html')": "https://www.randomservices.org/random/apps/BetaEstimate.html",
        "../special/Pareto.html": "https://www.randomservices.org/random/special/Pareto.html",
        "JavaScript:openAncillary('../biographies/Pareto.html')": "https://www.randomservices.org/random/biographies/Pareto.html",
        "JavaScript:openAncillary('../apps/ParetoEstimate.html')": "https://www.randomservices.org/random/apps/ParetoEstimate.html",
        "../special/UniformContinuous.html": "https://www.randomservices.org/random/special/UniformContinuous.html",
        "JavaScript:openAncillary('../apps/UniformEstimate.html')": "https://www.randomservices.org/random/apps/UniformEstimate.html",
        "../urn/Hypergeometric.html": "https://www.randomservices.org/random/urn/Hypergeometric.html",
        "../special/GeneralExponential.html": "https://www.randomservices.org/random/special/GeneralExponential.html",
        "JavaScript:openAncillary('../apps/index.html')": "https://www.randomservices.org/random/apps/index.html",
        "JavaScript:openAncillary('../data/index.html')": "https://www.randomservices.org/random/data/index.html",
        "JavaScript:openAncillary('../biographies/index.html')": "https://www.randomservices.org/random/biographies/index.html",
    },
}

# Source defects require occurrence-specific href deltas because each original
# href also has one or more correct occurrences on the same page. Nine of the
# fourteen bounded repairs below are on the admitted Unbiased page.
# The element indices are over the source/target element streams after removal
# of the separately validated edition notice.
HREF_ELEMENT_DELTAS: dict[
    tuple[PurePosixPath, int], tuple[str, str]
] = {
    (PurePosixPath("random/sample/Variance.html"), 53): ("Variance.html", "#inf"),
    (PurePosixPath("random/sample/Variance.html"), 220): ("#spe1", "#spe2"),
    (PurePosixPath("random/sample/Variance.html"), 614): ("#prb4", "#prb3"),
    (PurePosixPath("random/sample/Covariance.html"), 233): ("#reg4", "#reg2"),
    (PurePosixPath("random/sample/Covariance.html"), 272): ("Covariance.html", "#des"),
    (PurePosixPath("random/point/Unbiased.html"), 119): ("#crb8", "#crb6"),
    (PurePosixPath("random/point/Unbiased.html"), 163): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 176): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 188): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 215): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 225): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 242): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Unbiased.html"), 246): ("#sam5", "#sam4"),
    (PurePosixPath("random/point/Unbiased.html"), 253): ("#crb3", "#crb2"),
    (PurePosixPath("random/point/Sufficient.html"), 398): ("#ber", "#par"),
    (PurePosixPath("random/point/Sufficient.html"), 223): ("Moments.html#poi", "Moments.html#o006.random.point.moments.section.poisson"),
}

# The frozen Sufficient page has two unlabelled section headings and one
# duplicate native id.  The localizer gives the headings stable native anchors
# and renames the second ``gam2`` to ``gam3``; these are the only non-prefix
# identifiers admitted by this verifier.
SUFFICIENT_ID_ADDITIONS = {
    (PurePosixPath("random/point/Sufficient.html"), 39, "the"),
    (PurePosixPath("random/point/Sufficient.html"), 161, "exa"),
}
SUFFICIENT_ID_RENAMES = {
    (PurePosixPath("random/point/Sufficient.html"), 298, "gam2", "gam3"),
}
SUFFICIENT_CLASS_CORRECTIONS = {
    (PurePosixPath("random/point/Sufficient.html"), 350, ("mian",), ("main",)),
}

CORRECTION_DELTAS = {
    (
        PurePosixPath("random/sample/Introduction.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
    (
        PurePosixPath("random/sample/Introduction.html"),
        "JavaScript:openAncillary('../data/1948Election.html')",
        "https://www.randomservices.org/random/data/Election1948.html",
    ),
    (
        PurePosixPath("random/sample/Introduction.html"),
        "../dist/discrete.html",
        "https://www.randomservices.org/random/dist/Discrete.html",
    ),
    (
        PurePosixPath("random/sample/Mean.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
    (
        PurePosixPath("random/sample/Variance.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
    (
        PurePosixPath("random/sample/OrderStatistics.html"),
        "JavaScript:openAncillary('../data/Fisher.html')",
        "https://www.randomservices.org/random/data/Iris.html",
    ),
}

NOTICE_MARKUP_SHA256 = {
    PurePosixPath("random/sample/index.html"): "dc2b63db3864d3b2d9d2937269badca5ba6cbac0046482c03385aca0cb7bd255",
    PurePosixPath("random/sample/Introduction.html"): "64ad3ed4c57ffe8c0c91fae7047ba7d57399538bef9f7beae730e1fa4f4fa931",
    PurePosixPath("random/sample/Mean.html"): "b5dbee259ec1dd62c84f5d776320e15142359cc401afa413f9a2524f906fb275",
    PurePosixPath("random/sample/LLN.html"): "eeeac67515ebb62fe5c8f27cf428698ef9c3ec6c64628f0d3d160d98d81237c3",
    PurePosixPath("random/sample/CLT.html"): "9c1477ecc143e8a9bf20f6e0b6239b07d2dad564330df271690796289fa94ac0",
    PurePosixPath("random/sample/Variance.html"): "d1884c02cc756c0d44493d883eddf398dde3ad6f334691ccb3e33c5741b4504a",
    PurePosixPath("random/sample/OrderStatistics.html"): "3951beb5dc62b6796a5fda4afe5472c0b25a516294fb7e3dcc4a40764d0d726e",
    PurePosixPath("random/sample/Covariance.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/sample/Normal.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/index.html"): "5e06080b66862d770e89a0692ad72c347e52055448843e60d132e72aa2fb3e8f",
    PurePosixPath("random/point/Estimators.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/Moments.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/Likelihood.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/Bayes.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/Unbiased.html"): "eafff6cf003edc517cbc99727456b283de19cff49e07d20b10fea57dca0f8a3d",
    PurePosixPath("random/point/Sufficient.html"): "e05998dbc797a6a347ea25c3d38230297a352c0c749e3eac5a5ee0d4c3c50c47",
    PurePosixPath("random/interval/index.html"): "423da648600a2addb7cd91961a2c703458977f313bb72b203b64e45dd5ee3a9e",
    PurePosixPath("random/interval/Introduction.html"): "5ccdab4084043c1bc343dc05b9432c579ca039f5ce614cab8c14b95b1d0de99e",
    PurePosixPath("random/interval/Normal.html"): "01c5d127599821665ddf14d7cdfa8ec4436f1890132c256f8323888f8c0b4157",
    PurePosixPath("random/interval/Bernoulli.html"): "c0bc29c0d3e40f297c98497194071a4ad65d3f8ed305ea9ac0ccbe79f1af28e9",
    PurePosixPath("random/interval/BivariateNormal.html"): "5e2ba6a35ba3f3dfe00d40e610f13ab442ef7ac00a446bab017b96da5fb0f57c",
    PurePosixPath("random/interval/Bayes.html"): "8e92ce4d061d06c2b39cd110b3f933357237a79f23356ff65bb401e08e83945b",
    PurePosixPath("random/hypothesis/index.html"): "3e5edd78f8638d493625dd766cea1f463ef08b5fa40d7d9bd88081836bee599c",
    PurePosixPath("random/hypothesis/Introduction.html"): "82494825251a35253a6a24d3dc6b058f66005b06df5a4d497191daf9ad5b3e26",
    PurePosixPath("random/hypothesis/Normal.html"): "01396f2e25457e3ecf1f6226e765d04adea017213ba54d21d8b1eab640987a3d",
    PurePosixPath("random/hypothesis/Bernoulli.html"): "d8a2f6a18f85011ec775010cc9d0ae1335801d9c20b0d8a461372c23842fdbf5",
    PurePosixPath("random/hypothesis/BivariateNormal.html"): "01396f2e25457e3ecf1f6226e765d04adea017213ba54d21d8b1eab640987a3d",
    PurePosixPath("random/hypothesis/Likelihood.html"): "cc99bcf53d066f8f0492becc684f601aa5745b02df5cbd93fe079bdf586f5d69",
    PurePosixPath("random/hypothesis/ChiSquare.html"): "64360d3e1fef894468fdba21251f236cfb4efc6ede9e35bda0a0a7f84751d4ef",
}
NOTICE_LINKS = (
    "https://www.randomservices.org/random/",
    "https://creativecommons.org/licenses/by/2.0/",
    "https://www.randomservices.org/random/Credits.html",
    "https://creativecommons.org/licenses/by/1.0/",
)
NOTICE_TOKEN_COUNTS = {
    "Kyle Siegrist": 2,
    "Random": 2,
    "CC BY 2.0": 1,
    "CC BY 1.0": 1,
    "tidak didukung maupun disahkan": 1,
}
NOTICE_ALLOWED_TAGS = {"section", "p", "strong", "a", "span"}
NOTICE_FORBIDDEN_TAGS = {"script", "style", "iframe", "object", "embed", "base", "form"}
FETCH_ATTRIBUTES = {"src", "srcset", "poster", "data", "action", "formaction"}
REFERENCE_ATTRIBUTES = FETCH_ATTRIBUTES | {
    "href",
    "xlink:href",
    "background",
    "cite",
    "longdesc",
    "manifest",
    "usemap",
}

MATH_RE = re.compile(r"\\\((?:[^\\]|\\.)*?\\\)|\\\[(?:[^\\]|\\.)*?\\\]", re.DOTALL)
RAW_TEXT_RE = re.compile(r"<(script|style)\b[^>]*>(.*?)</\1\s*>", re.IGNORECASE | re.DOTALL)
RAW_MATH_ENV_RE = re.compile(
    r"\\begin\{(align\*?)\}.*?\\end\{\1\}", re.DOTALL
)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
CSS_URL_RE = re.compile(
    r"url\(\s*(?:(['\"])(.*?)\1|([^)]*?))\s*\)", re.IGNORECASE | re.DOTALL
)
CSS_IMPORT_RE = re.compile(r"@import\s+(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)
REMOTE_TEXT_RE = re.compile(r"(?i)(?:https?:)?//")
LOCAL_PATH_RE = re.compile(
    r"(?:[A-Za-z]:[\\/]+Users[\\/]+|file:(?:/|\\/){2,4}|/(?:home|Users|root)/)",
    re.IGNORECASE,
)
SECRET_RE = re.compile(
    r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*[^\s<]{12,}"
)
ENGLISH_DENY = (
    "Random Samples",
    "Expand Details",
    "Contract Details",
    ">Summary<",
    ">Topics<",
    ">Sources and Resources<",
    ">Examples<",
    ">Details:<",
    ">Designed experiment<",
    ">Observational study<",
    ">Point Estimation<",
    ">Estimators<",
    ">Basic Theory<",
    ">Computational Exercises<",
    ">Simulation Exercises<",
    ">Data Analysis Exercises<",
    ">Set Estimation<",
    ">Hypothesis Testing<",
    ">Likelihood Ratio Tests<",
    ">Applications<",
    "Suppose that ",
    "Properties of ",
)

# These exact non-fetching metadata links are already part of the approved
# href delta set. All fetching link relations remain forbidden remotely.
EXACT_EXTERNAL_METADATA_LINKS = {
    ("random/sample/index.html", "https://www.randomservices.org/random/index.html", "contents"),
    ("random/sample/index.html", "https://www.randomservices.org/random/special/index.html", "previous"),
    ("random/point/index.html", "https://www.randomservices.org/random/index.html", "contents"),
    ("random/interval/index.html", "https://www.randomservices.org/random/index.html", "contents"),
    ("random/hypothesis/index.html", "https://www.randomservices.org/random/index.html", "contents"),
    ("random/hypothesis/index.html", "https://www.randomservices.org/random/buffon/index.html", "next"),
    ("random/hypothesis/ChiSquare.html", "https://www.randomservices.org/random/buffon/index.html", "next"),
}


def fail(message: str) -> None:
    raise RuntimeError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read(path: Path) -> bytes:
    return build_pipeline.read_regular(path)


def check_translation_ledger() -> dict[PurePosixPath, dict[str, str]]:
    data = read(TRANSLATION_LEDGER)
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        fail(f"translation ledger is not UTF-8: {exc}")
    reader = csv.DictReader(text.splitlines())
    expected_header = (
        "ordinal",
        "source_path",
        "target_path",
        "status",
        "source_bytes",
        "source_sha256",
        "target_bytes",
        "target_sha256",
        "notes",
    )
    if tuple(reader.fieldnames or ()) != expected_header:
        fail(f"translation-ledger header differs: {reader.fieldnames}")
    rows = list(reader)
    ordinals = [int(row["ordinal"]) for row in rows]
    paths = tuple(PurePosixPath(row["source_path"]) for row in rows)
    if ordinals != list(range(1, 30)) or paths != PAIRS:
        fail(
            "translation ledger is not the exact complete ordered 1-29 corpus: "
            f"ordinals={ordinals}; paths={[path.as_posix() for path in paths]}"
        )
    result: dict[PurePosixPath, dict[str, str]] = {}
    for ordinal, rel, row in zip(ordinals, paths, rows):
        if row["status"] != "complete":
            fail(f"translation-ledger ordinal {ordinal} is not complete: {rel}")
        expected_target_path = f"source/id-ID/{rel.as_posix()}"
        if row["target_path"] != expected_target_path:
            fail(
                f"translation-ledger target path differs at ordinal {ordinal}: "
                f"{row['target_path']!r} != {expected_target_path!r}"
            )
        source_data = read(AUTHORITY / Path(rel.as_posix()))
        target_data = read(TARGET / Path(rel.as_posix()))
        if (
            int(row["source_bytes"]) != len(source_data)
            or row["source_sha256"] != sha256_bytes(source_data)
        ):
            fail(f"translation-ledger authority identity differs at ordinal {ordinal}: {rel}")
        if (
            int(row["target_bytes"]) != len(target_data)
            or row["target_sha256"] != sha256_bytes(target_data)
        ):
            fail(f"translation-ledger target identity differs at ordinal {ordinal}: {rel}")
        if not row["notes"].strip():
            fail(f"translation-ledger notes are empty at ordinal {ordinal}: {rel}")
        result[rel] = row
    return result


def soup(data: bytes, label: str, *, parser: str = "lxml") -> BeautifulSoup:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        fail(f"non-UTF-8 document {label}: {exc}")
    parsed = BeautifulSoup(text, parser)
    if parser == "lxml":
        if len(parsed.find_all("html")) != 1 or len(parsed.find_all("head")) != 1 or len(parsed.find_all("body")) != 1:
            fail(f"incomplete or multiply rooted HTML document: {label}")
    return parsed


def hierarchy_signature(node: Tag | BeautifulSoup) -> tuple[Any, ...]:
    children = tuple(hierarchy_signature(child) for child in node.children if isinstance(child, Tag))
    if isinstance(node, Tag):
        return (node.name, children)
    return children


def math_spans(text: str) -> list[str]:
    """Extract TeX without swallowing HTML after a malformed display opener.

    The frozen Mean authority contains one proved ``\\[`` display that reaches
    ``</p>`` without ``\\]``.  A cross-document regex would absorb translated
    prose until a later close and cannot prove protected-byte equality.  At
    that exact kind of malformed surface the paragraph boundary is used as the
    terminus, preserving the defect while keeping subsequent TeX comparable.
    """
    spans: list[str] = []
    cursor = 0
    while True:
        inline = text.find(r"\(", cursor)
        display = text.find(r"\[", cursor)
        starts = [
            (value, marker)
            for value, marker in ((inline, r"\("), (display, r"\["))
            if value >= 0
        ]
        if not starts:
            break
        start, opener = min(starts)
        closer = r"\)" if opener == r"\(" else r"\]"
        close = text.find(closer, start + 2)
        paragraph_end = text.find("</p>", start + 2)
        if paragraph_end >= 0 and (close < 0 or paragraph_end < close):
            spans.append(text[start:paragraph_end])
            cursor = paragraph_end
        elif close >= 0:
            spans.append(text[start : close + 2])
            cursor = close + 2
        else:
            spans.append(text[start:])
            break
    return spans


def normalize_authority_math(
    rel: PurePosixPath, spans: list[str]
) -> tuple[list[str], int, int]:
    """Apply declared source repairs and reader-language substitutions in TeX."""
    normalized = list(spans)
    corrected = 0
    for change in build_pipeline.PROTECTED_MATH_CORRECTIONS:
        if change["page"] != rel.as_posix() or change["surface"] != "math_span":
            continue
        old = change.get("span_old", change["old"])
        new = change.get("span_new", change["new"])
        expected = int(change["replacements"])
        span_index = change.get("span_index")
        selected: list[int]
        if span_index is None:
            selected = list(range(len(normalized)))
        else:
            selected = [int(span_index) - 1]
            if selected[0] < 0 or selected[0] >= len(normalized):
                fail(f"{rel}: protected TeX correction span index is out of range: {span_index}")
        observed = sum(normalized[index].count(old) for index in selected)
        if observed != expected:
            fail(
                f"{rel}: protected TeX correction authority count changed for {old!r}: "
                f"{observed} != {expected}"
            )
        for index in selected:
            normalized[index] = normalized[index].replace(old, new)
        corrected += observed
    localized = 0
    for change in build_pipeline.MATH_TEXT_LOCALIZATIONS:
        if change["page"] != rel.as_posix() or change["surface"] != "math_span":
            continue
        old = change["old"]
        new = change["new"]
        expected = int(change["replacements"])
        observed = sum(span.count(old) for span in normalized)
        if observed != expected:
            fail(
                f"{rel}: protected TeX localization authority count changed for {old!r}: "
                f"{observed} != {expected}"
            )
        normalized = [span.replace(old, new) for span in normalized]
        localized += observed
    return normalized, corrected, localized


def normalize_authority_raw_math(
    rel: PurePosixPath, environments: list[str]
) -> tuple[list[str], int]:
    """Apply only declared repairs inside undelimited align environments."""
    normalized = list(environments)
    corrected = 0
    for change in build_pipeline.PROTECTED_MATH_CORRECTIONS:
        if change["page"] != rel.as_posix() or change["surface"] != "raw_math_environment":
            continue
        old = change["old"]
        new = change["new"]
        expected = int(change["replacements"])
        observed = sum(environment.count(old) for environment in normalized)
        if observed != expected:
            fail(
                f"{rel}: raw-math correction authority count changed for {old!r}: "
                f"{observed} != {expected}"
            )
        normalized = [environment.replace(old, new) for environment in normalized]
        corrected += expected
    return normalized, corrected


def element_stream(parsed: BeautifulSoup) -> list[Tag]:
    return list(parsed.find_all(True))


def validate_allowlist() -> None:
    if len(PAIRS) != 29 or len(set(PAIRS)) != 29:
        fail("complete Random corpus is not exactly 29 unique pages")
    if tuple(build_pipeline.TARGETS) != PAIRS:
        fail("build target order differs from the exact translation-ledger 1-29 order")
    if set(HREF_DELTA_ALLOWLIST) != set(LEGACY_PAIRS):
        fail("detailed href-delta allowlist differs from its exact ordinal 1-16 scope")
    if set(PAGE_EXPECTATIONS) != set(PAIRS) or len(PAGE_EXPECTATION_ROWS) != len(PAIRS):
        fail("page-expectation set differs from the exact 29-page corpus")
    if set(HREF_PAIR_EXPECTATIONS) != set(PAIRS):
        fail("href-pair fingerprint set differs from the exact 29-page corpus")
    if set(NOTICE_MARKUP_SHA256) != set(PAIRS):
        fail("edition-notice hash page set differs from the exact 29-page corpus")
    if TARGET_ELEMENT_INSERTIONS != {
        PurePosixPath("random/point/Estimators.html"): (54, "summary", {}),
        PurePosixPath("random/interval/BivariateNormal.html"): (56, "p", {}),
    }:
        fail("exact topology insertion declarations differ")
    for (rel, element_index, attribute), (original, target_value) in ELEMENT_ATTRIBUTE_DELTAS.items():
        if (
            rel not in PAIRS
            or element_index < 1
            or attribute not in REFERENCE_ATTRIBUTES
            or not original
            or not target_value
        ):
            fail(f"invalid exact attribute-delta declaration: {rel} element {element_index}")
    for rel, mapping in HREF_DELTA_ALLOWLIST.items():
        if len(mapping) != len(set(mapping)):
            fail(f"duplicate href-delta key for {rel}")
        for original, target in mapping.items():
            if not original or urlparse(target).scheme != "https":
                fail(f"non-HTTPS or empty exact href delta for {rel}: {original!r}->{target!r}")
    for (rel, element_index), (original, target) in HREF_ELEMENT_DELTAS.items():
        if rel not in LEGACY_PAIRS or element_index < 1 or not original or not target:
            fail(f"invalid occurrence-specific href delta: {rel} element {element_index}")
        if _external_url(target):
            _validate_https(target, f"occurrence-specific href delta {rel} element {element_index}")
    actual_corrections = {
        (rel, original, target)
        for rel, mapping in HREF_DELTA_ALLOWLIST.items()
        for original, target in mapping.items()
        if (rel, original, target) in CORRECTION_DELTAS
    }
    if actual_corrections != CORRECTION_DELTAS:
        fail("the controlled filename/case corrections are not exactly allowlisted")
    for change in build_pipeline.TRANSPORT_HARDENING:
        rel = PurePosixPath(change["page"])
        if HREF_DELTA_ALLOWLIST.get(rel, {}).get(change["original_href"]) != change["target_href"]:
            fail("transport-only hardening and href-delta allowlist disagree")


def validate_notice(notice: Tag, rel: PurePosixPath) -> dict[str, Any]:
    if notice.name != "section":
        fail(f"{rel}: edition notice is not a section")
    if notice.attrs != {"class": ["edition-notice"], "data-o006-edition-notice": "v1"}:
        fail(f"{rel}: edition notice root attributes differ")
    paragraph_hierarchy: list[tuple[Any, ...]] = [
        ("p", (("strong", ()), ("a", ()))),
        ("p", (("a", ()), ("a", ()), ("a", ()))),
    ]
    if rel == PurePosixPath("random/hypothesis/index.html"):
        paragraph_hierarchy.append(("p", ()))
    elif rel.parts[:2] == ("random", "hypothesis"):
        paragraph_hierarchy.insert(1, ("p", ()))
    if rel == PurePosixPath("random/hypothesis/ChiSquare.html"):
        paragraph_hierarchy[0] = (
            "p",
            (("strong", ()), ("a", ()), ("span", ())),
        )
    expected_hierarchy = ("section", tuple(paragraph_hierarchy))
    if hierarchy_signature(notice) != expected_hierarchy:
        fail(f"{rel}: edition notice hierarchy differs")
    if notice.find_all(string=lambda value: isinstance(value, Comment)):
        fail(f"{rel}: comments are forbidden in the edition notice")
    for tag in notice.find_all(True):
        if tag.name in NOTICE_FORBIDDEN_TAGS or tag.name not in NOTICE_ALLOWED_TAGS:
            fail(f"{rel}: forbidden edition-notice element: {tag.name}")
        for attr in tag.attrs:
            lower = attr.lower()
            if lower.startswith("on") or lower in FETCH_ATTRIBUTES or lower in {"style", "srcdoc"}:
                fail(f"{rel}: active/fetching edition-notice attribute: {tag.name}[{attr}]")
        if tag.name == "section":
            allowed = {"class", "data-o006-edition-notice"}
        elif tag.name == "a":
            allowed = {"href"}
        elif tag.name == "span" and rel == PurePosixPath("random/hypothesis/ChiSquare.html"):
            allowed = {"class"}
            if tag.attrs != {"class": ["math-inline"]}:
                fail(f"{rel}: exact passive notice span attributes differ")
        else:
            allowed = set()
        if set(tag.attrs) != allowed:
            fail(f"{rel}: edition-notice attribute set differs on {tag.name}")
    links = tuple(str(link.get("href")) for link in notice.find_all("a"))
    if links != NOTICE_LINKS:
        fail(f"{rel}: edition-notice links differ")
    text = notice.get_text(" ", strip=True)
    for token, expected_count in NOTICE_TOKEN_COUNTS.items():
        if text.count(token) != expected_count:
            fail(f"{rel}: edition-notice token count differs for {token!r}")
    markup = notice.decode(formatter="minimal").encode("utf-8")
    expected_sha256 = NOTICE_MARKUP_SHA256[rel]
    if expected_sha256 == "PENDING_UNBIASED_NOTICE_MARKUP_SHA256":
        fail(f"{rel}: edition-notice hash is pending target generation")
    if sha256_bytes(markup) != expected_sha256:
        fail(f"{rel}: edition-notice bounded markup differs")
    return {"bytes": len(markup), "sha256": sha256_bytes(markup), "links": len(links)}


def paired_core_elements(
    rel: PurePosixPath, source_tags: list[Tag], target_tags: list[Tag]
) -> list[tuple[int, Tag, Tag]]:
    insertion = TARGET_ELEMENT_INSERTIONS.get(rel)
    comparable_target = list(target_tags)
    if insertion is None:
        if len(source_tags) != len(comparable_target):
            fail(f"{rel}: undeclared core element-count delta")
    else:
        target_index, expected_name, expected_attrs = insertion
        if len(comparable_target) != len(source_tags) + 1:
            fail(f"{rel}: declared one-element topology repair is not the sole element delta")
        inserted = comparable_target[target_index - 1]
        if inserted.name != expected_name or dict(inserted.attrs) != expected_attrs:
            fail(
                f"{rel}: declared target element {target_index} differs: "
                f"{inserted.name} {inserted.attrs}"
            )
        del comparable_target[target_index - 1]
    source_names = [tag.name for tag in source_tags]
    target_names = [tag.name for tag in comparable_target]
    if source_names != target_names:
        fail(f"{rel}: tag order changed beyond the exact declared topology repair")
    return [
        (index, source_tag, target_tag)
        for index, (source_tag, target_tag) in enumerate(
            zip(source_tags, comparable_target), start=1
        )
    ]


def _resolved_random_html(rel: PurePosixPath, href: str) -> PurePosixPath | None:
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc:
        if parsed.scheme.lower() not in {"http", "https"}:
            return None
        if (parsed.hostname or "").lower() != "www.randomservices.org":
            return None
        path = unquote(parsed.path)
        if not path.startswith("/random/") or not path.lower().endswith(".html"):
            return None
        return PurePosixPath(path.lstrip("/"))
    path, _fragment = urldefrag(href)
    if not path.lower().endswith(".html"):
        return None
    normalized = posixpath.normpath(posixpath.join(rel.parent.as_posix(), path))
    if normalized.startswith("../"):
        return None
    return PurePosixPath(normalized)


def validate_href_semantics(
    rel: PurePosixPath, element_index: int, source_tag: Tag, target_tag: Tag
) -> None:
    source_href = source_tag.get("href")
    target_href = target_tag.get("href")
    if target_href is None:
        return
    target_value = str(target_href)
    parsed = urlparse(target_value)
    if parsed.scheme.lower() == "javascript":
        fail(f"{rel}: executable href remains at paired element {element_index}")
    target_core = rel if target_value.startswith("#") else _resolved_random_html(rel, target_value)
    is_external = bool(parsed.scheme or parsed.netloc)
    if is_external:
        _validate_https(target_value, f"{rel} paired element {element_index}")
        if target_core in PAIRS:
            fail(
                f"{rel}: admitted core link remains upstream at paired element "
                f"{element_index}: {target_value}"
            )
    elif target_core is not None and target_core not in PAIRS:
        fail(
            f"{rel}: local HTML link is outside the admitted 29-page corpus at "
            f"paired element {element_index}: {target_value}"
        )

    if source_href is not None:
        source_value = str(source_href)
        source_core = _resolved_random_html(rel, source_value)
        if source_core in PAIRS and (is_external or target_core not in PAIRS):
            fail(
                f"{rel}: source core link was not retained as a local admitted link at "
                f"paired element {element_index}: {source_value!r}->{target_value!r}"
            )
        if source_value.lower().startswith("javascript:openancillary("):
            if not is_external:
                fail(f"{rel}: ancillary link is not external HTTPS at element {element_index}")
            hostname = (parsed.hostname or "").lower()
            if hostname != "www.randomservices.org" or not parsed.path.startswith(
                ("/random/apps/", "/random/data/", "/random/biographies/")
            ):
                fail(
                    f"{rel}: ancillary link is not on its official surface at element "
                    f"{element_index}: {target_value}"
                )
    classes = {str(value) for value in (target_tag.get("class") or [])}
    if "ancillary" in classes and (
        not is_external or (parsed.hostname or "").lower() != "www.randomservices.org"
    ):
        fail(f"{rel}: ancillary-class link is not official HTTPS at element {element_index}")


def href_pair_fingerprints(
    rel: PurePosixPath, pairs: list[tuple[int, Tag, Tag]]
) -> dict[str, Any]:
    records: list[list[Any]] = []
    deltas: list[list[Any]] = []
    for index, source_tag, target_tag in pairs:
        source_href = source_tag.get("href")
        target_href = target_tag.get("href")
        if source_href is not None or target_href is not None:
            record = [index, source_href, target_href]
            records.append(record)
            if source_href != target_href:
                deltas.append(record)
        validate_href_semantics(rel, index, source_tag, target_tag)
    records_data = (
        json.dumps(records, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    deltas_data = (
        json.dumps(deltas, ensure_ascii=False, separators=(",", ":")) + "\n"
    ).encode("utf-8")
    expected_records, expected_records_sha, expected_deltas, expected_deltas_sha = (
        HREF_PAIR_EXPECTATIONS[rel]
    )
    actual = (len(records), sha256_bytes(records_data), len(deltas), sha256_bytes(deltas_data))
    expected = (
        expected_records,
        expected_records_sha,
        expected_deltas,
        expected_deltas_sha,
    )
    if actual != expected:
        fail(f"{rel}: exact href-pair fingerprint differs: {actual} != {expected}")
    return {
        "href_pair_occurrences": len(records),
        "href_pair_sha256": actual[1],
        "href_delta_entries": len({(record[1], record[2]) for record in deltas}),
        "href_delta_occurrences": len(deltas),
        "href_delta_sha256": actual[3],
    }


def compare_pair(rel: PurePosixPath) -> dict[str, Any]:
    expectation = PAGE_EXPECTATIONS[rel]
    source_data = read(AUTHORITY / Path(rel.as_posix()))
    target_data = read(TARGET / Path(rel.as_posix()))
    reader_data = read(READER / Path(rel.as_posix()))
    if reader_data != target_data:
        fail(f"{rel}: built reader is not byte-identical to the translation target")

    source = soup(source_data, f"source:{rel}")
    target = soup(target_data, f"target:{rel}")
    notices = target.select('[data-o006-edition-notice="v1"]')
    if len(notices) != 1:
        fail(f"{rel}: expected exactly one edition notice, found {len(notices)}")
    notice_result = validate_notice(notices[0], rel)
    notices[0].decompose()

    source_hierarchy = hierarchy_signature(source)
    target_hierarchy = hierarchy_signature(target)
    if (
        rel in LEGACY_PAIRS
        and rel not in TARGET_ELEMENT_INSERTIONS
        and source_hierarchy != target_hierarchy
    ):
        fail(f"{rel}: hierarchical DOM signature differs after validated notice removal")

    source_tags = element_stream(source)
    target_tags = element_stream(target)
    if len(source_tags) != int(expectation["source_elements"]):
        fail(f"{rel}: source element census differs: {len(source_tags)}")
    if len(target_tags) != int(expectation["target_elements"]):
        fail(f"{rel}: target core element census differs: {len(target_tags)}")
    paired_tags = paired_core_elements(rel, source_tags, target_tags)

    source_text = source_data.decode("utf-8")
    target_text = target_data.decode("utf-8")
    source_raw = [(name.lower(), body) for name, body in RAW_TEXT_RE.findall(source_text)]
    target_raw = [(name.lower(), body) for name, body in RAW_TEXT_RE.findall(target_text)]
    if source_raw != target_raw:
        fail(f"{rel}: script/style raw text differs")
    if len(source_raw) != int(expectation["raw_script_style_blocks"]):
        fail(f"{rel}: script/style block census differs: {len(source_raw)}")

    source_math = math_spans(source_text)
    target_math = math_spans(target_text)
    expected_math_count = int(expectation["math_spans"])
    if len(source_math) != expected_math_count or len(target_math) != expected_math_count:
        fail(
            f"{rel}: protected TeX census differs: "
            f"{len(source_math)}->{len(target_math)} != {expected_math_count}"
        )
    canonical_source_math = [re.sub(r"\s+", "", span) for span in source_math]
    canonical_target_math = [re.sub(r"\s+", "", span) for span in target_math]
    target_math_sha256 = sha256_bytes("\n".join(canonical_target_math).encode("utf-8"))
    if target_math_sha256 != expectation["target_math_sha256"]:
        fail(f"{rel}: exact canonical target-TeX sequence fingerprint differs")
    math_delta_spans = sum(
        source_span != target_span
        for source_span, target_span in zip(canonical_source_math, canonical_target_math)
    )
    protected_math_replacements = 0
    math_text_localization_replacements = 0
    if rel in LEGACY_PAIRS:
        (
            expected_math,
            protected_math_replacements,
            math_text_localization_replacements,
        ) = normalize_authority_math(rel, source_math)
        if expected_math != target_math:
            fail(
                f"{rel}: exact declared TeX/math sequence changed "
                f"({len(source_math)} vs {len(target_math)})"
            )

    source_raw_math = [match.group(0) for match in RAW_MATH_ENV_RE.finditer(source_text)]
    target_raw_math = [match.group(0) for match in RAW_MATH_ENV_RE.finditer(target_text)]
    expected_raw_count = int(expectation["raw_math_environments"])
    if len(source_raw_math) != expected_raw_count or len(target_raw_math) != expected_raw_count:
        fail(
            f"{rel}: raw align-environment census differs: "
            f"{len(source_raw_math)}->{len(target_raw_math)} != {expected_raw_count}"
        )
    source_raw_math_sha256 = sha256_bytes("\n".join(source_raw_math).encode("utf-8"))
    target_raw_math_sha256 = sha256_bytes("\n".join(target_raw_math).encode("utf-8"))
    if target_raw_math_sha256 != expectation["target_raw_math_sha256"]:
        fail(f"{rel}: exact target raw align-environment fingerprint differs")
    raw_math_delta_environments = sum(
        source_environment != target_environment
        for source_environment, target_environment in zip(source_raw_math, target_raw_math)
    )
    raw_math_replacements = 0
    if rel in {
        PurePosixPath("random/point/Bayes.html"),
        PurePosixPath("random/point/Unbiased.html"),
    }:
        expected_raw_math, raw_math_replacements = normalize_authority_raw_math(
            rel, source_raw_math
        )
        if expected_raw_math != target_raw_math:
            fail(
                f"{rel}: exact raw align-environment sequence changed "
                f"({len(source_raw_math)} vs {len(target_raw_math)})"
            )
    protected_math_replacements += raw_math_replacements

    allowed_attr_deltas = {"lang", "title", "alt", "content", "id", "href"}
    page_allowlist = HREF_DELTA_ALLOWLIST.get(rel, {})
    seen_deltas: set[tuple[str, str]] = set()
    seen_element_deltas: set[tuple[int, str, str]] = set()
    seen_attribute_deltas: set[tuple[int, str, Any, Any]] = set()
    href_delta_occurrences = 0
    for index, source_tag, target_tag in paired_tags:
        all_keys = set(source_tag.attrs) | set(target_tag.attrs)
        for key in all_keys:
            source_value = source_tag.attrs.get(key)
            target_value = target_tag.attrs.get(key)
            if source_value == target_value:
                if (rel, index, key) in ELEMENT_ATTRIBUTE_DELTAS:
                    fail(f"{rel}: exact {key} delta was not applied at element {index}")
                if key == "href":
                    if (rel, index) in HREF_ELEMENT_DELTAS:
                        fail(f"{rel}: occurrence-specific href delta was not applied at element {index}")
                    if str(source_value) in page_allowlist:
                        fail(f"{rel}: allowlisted href delta was not applied at element {index}")
                continue
            exact_attribute_delta = ELEMENT_ATTRIBUTE_DELTAS.get((rel, index, key))
            if exact_attribute_delta is not None:
                if (source_value, target_value) != exact_attribute_delta:
                    fail(
                        f"{rel}: exact {key} delta differs at element {index}: "
                        f"{source_value!r}->{target_value!r}"
                    )
                seen_attribute_deltas.add((index, key, source_value, target_value))
                continue
            if key == "class":
                if (rel, index, tuple(source_value or ()), tuple(target_value or ())) in SUFFICIENT_CLASS_CORRECTIONS:
                    continue
                fail(f"{rel}: unexplained class delta at element {index}")
            if key not in allowed_attr_deltas:
                fail(f"{rel}: unexplained attr delta at element {index}: {key}")
            if key == "lang" and not (source_value == "en" and target_value == "id-ID"):
                fail(f"{rel}: invalid lang delta {source_value!r}->{target_value!r}")
            elif key == "id":
                if source_value is not None:
                    if (rel, index, str(source_value), str(target_value)) not in SUFFICIENT_ID_RENAMES:
                        fail(f"{rel}: existing id changed at element {index}")
                elif (rel, index, str(target_value)) not in SUFFICIENT_ID_ADDITIONS:
                    if not isinstance(target_value, str) or not target_value.startswith("o006.random."):
                        fail(f"{rel}: invalid additive stable id at element {index}: {target_value!r}")
            elif key == "href":
                href_delta_occurrences += 1
                if rel not in LEGACY_PAIRS:
                    continue
                original = str(source_value)
                element_delta = HREF_ELEMENT_DELTAS.get((rel, index))
                if element_delta is not None:
                    expected_original, expected_target = element_delta
                    if original != expected_original or target_value != expected_target:
                        fail(
                            f"{rel}: occurrence-specific href delta differs at element {index}: "
                            f"{source_value!r}->{target_value!r}"
                        )
                    seen_element_deltas.add((index, expected_original, expected_target))
                else:
                    expected = page_allowlist.get(original)
                    if expected is None or target_value != expected:
                        fail(
                            f"{rel}: href delta not exactly allowlisted at element {index}: "
                            f"{source_value!r}->{target_value!r}"
                        )
                    seen_deltas.add((original, expected))
    expected_deltas = set(page_allowlist.items())
    if seen_deltas != expected_deltas:
        missing = sorted(expected_deltas - seen_deltas)
        extra = sorted(seen_deltas - expected_deltas)
        fail(f"{rel}: href-delta use mismatch; missing={missing}; extra={extra}")
    expected_element_deltas = {
        (index, original, target)
        for (page, index), (original, target) in HREF_ELEMENT_DELTAS.items()
        if page == rel
    }
    if seen_element_deltas != expected_element_deltas:
        missing = sorted(expected_element_deltas - seen_element_deltas)
        extra = sorted(seen_element_deltas - expected_element_deltas)
        fail(f"{rel}: occurrence-specific href-delta mismatch; missing={missing}; extra={extra}")
    expected_attribute_deltas = {
        (index, key, original, target_value)
        for (page, index, key), (original, target_value) in ELEMENT_ATTRIBUTE_DELTAS.items()
        if page == rel
    }
    if seen_attribute_deltas != expected_attribute_deltas:
        fail(f"{rel}: exact non-href attribute-delta inventory differs")
    href_result = href_pair_fingerprints(rel, paired_tags)
    if href_delta_occurrences != int(href_result["href_delta_occurrences"]):
        fail(f"{rel}: attribute and href-fingerprint delta counts disagree")

    full = soup(target_data, f"target:{rel}:full")
    ids = [str(tag["id"]) for tag in full.find_all(attrs={"id": True})]
    if len(ids) != len(set(ids)):
        duplicates = sorted(key for key, count in Counter(ids).items() if count > 1)
        fail(f"{rel}: duplicate target IDs: {duplicates}")
    if full.html is None or full.html.get("lang") != "id-ID":
        fail(f"{rel}: html lang is not id-ID")
    if full.find("meta", attrs={"charset": re.compile("utf-8", re.I)}) is None:
        fail(f"{rel}: UTF-8 meta declaration absent")
    units = full.select("div.unit")
    details = full.find_all("details")
    for unit in units:
        if not unit.get("id"):
            fail(f"{rel}: unit without stable id")
    if len(units) != int(expectation["units"]) or len(details) != int(expectation["details"]):
        fail(f"{rel}: unit/disclosure census differs: {len(units)}/{len(details)}")
    for disclosure in details:
        summaries = disclosure.find_all("summary", recursive=False)
        if len(summaries) != 1 or summaries[0].get_text(" ", strip=True) != "Rincian:":
            fail(f"{rel}: disclosure lacks its exact accessible Indonesian summary")
    for image in full.find_all("img"):
        alt = image.get("alt")
        if not isinstance(alt, str) or not alt.strip():
            fail(f"{rel}: image lacks useful nonempty alternative text")
    if len(ids) != int(expectation["ids"]) or expectation["page_id"] not in ids:
        fail(f"{rel}: exact ID census or stable page ID differs")
    if LOCAL_PATH_RE.search(target_text) or SECRET_RE.search(target_text):
        fail(f"{rel}: local path or secret-shaped text detected")
    for phrase in ENGLISH_DENY:
        if phrase in target_text:
            fail(f"{rel}: active English UI/prose residue: {phrase}")

    hierarchy_bytes = json.dumps(source_hierarchy, separators=(",", ":")).encode("utf-8")
    target_hierarchy_bytes = json.dumps(target_hierarchy, separators=(",", ":")).encode("utf-8")
    return {
        "source_bytes": len(source_data),
        "source_sha256": sha256_bytes(source_data),
        "target_bytes": len(target_data),
        "target_sha256": sha256_bytes(target_data),
        "reader_bytes": len(reader_data),
        "reader_sha256": sha256_bytes(reader_data),
        "reader_target_byte_identical": True,
        "elements": len(source_tags),
        "target_core_elements": len(target_tags),
        "hierarchy_sha256": sha256_bytes(hierarchy_bytes),
        "target_hierarchy_sha256": sha256_bytes(target_hierarchy_bytes),
        "declared_target_element_insertions": 1 if rel in TARGET_ELEMENT_INSERTIONS else 0,
        "raw_script_style_blocks": len(source_raw),
        "math_spans": len(source_math),
        "target_math_sha256": target_math_sha256,
        "math_delta_spans": math_delta_spans,
        "raw_math_environments": len(source_raw_math),
        "raw_math_sha256": source_raw_math_sha256,
        "target_raw_math_sha256": target_raw_math_sha256,
        "raw_math_delta_environments": raw_math_delta_environments,
        "protected_math_replacements": protected_math_replacements,
        "math_text_localization_replacements": math_text_localization_replacements,
        "href_delta_entries": (
            len(seen_deltas) + len(seen_element_deltas)
            if rel in LEGACY_PAIRS
            else int(href_result["href_delta_entries"])
        ),
        "href_delta_occurrences": href_delta_occurrences,
        "href_pair_occurrences": int(href_result["href_pair_occurrences"]),
        "href_pair_sha256": href_result["href_pair_sha256"],
        "href_delta_sha256": href_result["href_delta_sha256"],
        "occurrence_specific_href_deltas": len(seen_element_deltas),
        "units": len(units),
        "details": len(details),
        "ids": len(ids),
        "edition_notice": notice_result,
    }


def _attribute_text(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return " ".join(str(item) for item in value)
    return str(value)


def _external_url(value: str) -> bool:
    parsed = urlparse(value)
    return bool(parsed.scheme or parsed.netloc)


def _validate_https(value: str, label: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme.lower() != "https" or not parsed.hostname or parsed.username or parsed.password:
        fail(f"external navigation must be credential-free HTTPS: {label}: {value}")


def _local_target(page: Path, value: str) -> tuple[Path, str]:
    if not value or "\x00" in value or "\\" in value:
        fail(f"noncanonical local reference in {page}: {value!r}")
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        fail(f"not a local reference in {page}: {value}")
    decoded_path = unquote(parsed.path)
    if decoded_path != parsed.path or "\\" in decoded_path or "\x00" in decoded_path:
        fail(f"encoded/noncanonical local path in {page}: {value}")
    if decoded_path.startswith("/"):
        target = READER / decoded_path.lstrip("/")
    elif decoded_path:
        target = page.parent / decoded_path
    else:
        target = page
    resolved = target.resolve(strict=False)
    try:
        resolved.relative_to(READER.resolve())
    except ValueError:
        fail(f"local reference escapes reader: {page.relative_to(READER)} -> {value}")
    build_pipeline.ensure_regular(resolved, reject_hardlinks=True)
    return resolved, unquote(parsed.fragment)


def _check_local_reference(
    page: Path,
    value: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    target, fragment = _local_target(page, value)
    counts["local_refs"] += 1
    if fragment:
        if target.suffix.lower() not in {".html", ".htm", ".svg"}:
            fail(f"fragment targets a non-document: {page.relative_to(READER)} -> {value}")
        target_doc = parsed_cache.get(target)
        if target_doc is None:
            parser = "xml" if target.suffix.lower() == ".svg" else "lxml"
            target_doc = soup(read(target), f"reader-fragment:{target}", parser=parser)
            parsed_cache[target] = target_doc
        if target_doc.find(id=fragment) is None:
            fail(f"broken fragment: {page.relative_to(READER)} -> {value}")
        counts["fragments"] += 1


def _css_references(css: str) -> list[str]:
    without_comments = CSS_COMMENT_RE.sub("", css)
    refs = []
    for match in CSS_URL_RE.finditer(without_comments):
        refs.append((match.group(2) if match.group(1) else match.group(3)).strip())
    refs.extend(match.group(2).strip() for match in CSS_IMPORT_RE.finditer(without_comments))
    return refs


def _check_css(
    owner: Path,
    css: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    for value in _css_references(css):
        if not value:
            fail(f"empty CSS URL in {owner.relative_to(READER)}")
        if _external_url(value):
            fail(f"remote CSS url/@import is forbidden: {owner.relative_to(READER)} -> {value}")
        _check_local_reference(owner, value, parsed_cache, counts)
        counts["css_refs"] += 1


def _check_html_reference(
    page: Path,
    tag: Tag,
    attr: str,
    value: str,
    parsed_cache: dict[Path, BeautifulSoup],
    counts: Counter[str],
) -> None:
    if _external_url(value):
        if tag.name == "a" and attr == "href":
            _validate_https(value, f"{page.relative_to(READER)} a[href]")
            counts["external_https_anchors"] += 1
            return
        if tag.name == "link" and attr == "href":
            rels = tuple(str(item).lower() for item in (tag.get("rel") or []))
            if len(rels) == 1 and (page.relative_to(READER).as_posix(), value, rels[0]) in EXACT_EXTERNAL_METADATA_LINKS:
                _validate_https(value, f"{page.relative_to(READER)} link[{rels[0]}]")
                counts["external_https_metadata_links"] += 1
                return
        fail(f"remote reference is forbidden outside an anchor href: {page.relative_to(READER)} {tag.name}[{attr}]={value}")
    _check_local_reference(page, value, parsed_cache, counts)


def check_reader_references() -> dict[str, int]:
    rows = build_pipeline.canonical_rows(READER)
    pages = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".html"]
    stylesheets = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".css"]
    svgs = [READER / rel for rel, _, _ in rows if PurePosixPath(rel).suffix.lower() == ".svg"]
    if not pages:
        fail("reader contains no HTML pages")
    parsed_cache: dict[Path, BeautifulSoup] = {}
    counts: Counter[str] = Counter()
    for page in pages:
        parsed_cache[page.resolve()] = soup(read(page), f"reader:{page.relative_to(READER)}")

    for page in pages:
        parsed = parsed_cache[page.resolve()]
        rel = page.relative_to(READER)
        if parsed.html is None or parsed.html.get("lang") != "id-ID":
            fail(f"reader page locale is not id-ID: {rel}")
        if parsed.find("meta", attrs={"charset": re.compile("utf-8", re.I)}) is None:
            fail(f"reader page lacks UTF-8 metadata: {rel}")
        ids = [str(tag["id"]) for tag in parsed.find_all(id=True)]
        if len(ids) != len(set(ids)):
            fail(f"reader page contains duplicate IDs: {rel}")
        if any(
            not isinstance(image.get("alt"), str) or not str(image.get("alt")).strip()
            for image in parsed.find_all("img")
        ):
            fail(f"reader page contains an image without useful alternative text: {rel}")
        for disclosure in parsed.find_all("details"):
            summaries = disclosure.find_all("summary", recursive=False)
            if len(summaries) != 1 or summaries[0].get_text(" ", strip=True) != "Rincian:":
                fail(f"reader page contains an inaccessible disclosure: {rel}")
        if parsed.find(["iframe", "object", "embed", "form"]) is not None:
            fail(f"active embedded/form surface is forbidden in offline reader: {rel}")
        page_text = read(page).decode("utf-8")
        if LOCAL_PATH_RE.search(page_text) or SECRET_RE.search(page_text):
            fail(f"reader page leaks a local path or secret-shaped text: {rel}")
        if parsed.find("base") is not None:
            fail(f"base element is forbidden: {rel}")
        for meta in parsed.find_all("meta"):
            if str(meta.get("http-equiv", "")).casefold() == "refresh":
                fail(f"meta refresh is forbidden: {page.relative_to(READER)}")
        for tag in parsed.find_all(True):
            for attr, raw_value in tag.attrs.items():
                attr_lower = attr.lower()
                value = _attribute_text(raw_value).strip()
                if attr_lower.startswith("on"):
                    # Event handlers are allowed only when byte-preserved by the
                    # authority comparison; neither generated page has one.
                    rel = PurePosixPath(page.relative_to(READER).as_posix())
                    if rel not in PAIRS:
                        fail(f"event handler in generated reader page: {page.relative_to(READER)} {attr}")
                if attr_lower == "style":
                    _check_css(page, value, parsed_cache, counts)
                if attr_lower == "srcset":
                    for candidate in value.split(","):
                        url = candidate.strip().split()[0] if candidate.strip() else ""
                        if not url:
                            fail(f"malformed srcset in {page.relative_to(READER)}")
                        _check_html_reference(page, tag, attr_lower, url, parsed_cache, counts)
                    continue
                if attr_lower in REFERENCE_ATTRIBUTES and value:
                    _check_html_reference(page, tag, attr_lower, value, parsed_cache, counts)
                elif REMOTE_TEXT_RE.search(value):
                    fail(f"remote URL outside a reference attribute: {page.relative_to(READER)} {tag.name}[{attr}]")
            if tag.name == "style":
                _check_css(page, tag.decode_contents(formatter=None), parsed_cache, counts)

    for stylesheet in stylesheets:
        _check_css(stylesheet, read(stylesheet).decode("utf-8"), parsed_cache, counts)

    for svg in svgs:
        parsed = soup(read(svg), f"reader-svg:{svg.relative_to(READER)}", parser="xml")
        for tag in parsed.find_all(True):
            for attr in ("href", "xlink:href"):
                value = tag.get(attr)
                if value:
                    if _external_url(str(value)):
                        fail(f"remote SVG reference is forbidden: {svg.relative_to(READER)} {attr}={value}")
                    _check_local_reference(svg, str(value), parsed_cache, counts)
            if tag.get("style"):
                _check_css(svg, str(tag["style"]), parsed_cache, counts)
        for style in parsed.find_all("style"):
            _check_css(svg, style.decode_contents(formatter=None), parsed_cache, counts)

    counts["html_pages"] = len(pages)
    counts["css_files"] = len(stylesheets)
    counts["svg_files"] = len(svgs)
    return dict(sorted(counts.items()))


def check_target_only_assets() -> list[dict[str, Any]]:
    expected = (
        (
            PurePosixPath("random/interval/Tails-id.svg"),
            2150,
            "b218a05a39687f1e5c7bf0a14c1702b49e6ce24129e378ede2bcfa7a9fe2c151",
        ),
    )
    results: list[dict[str, Any]] = []
    for rel, expected_bytes, expected_sha256 in expected:
        target_data = read(TARGET / Path(rel.as_posix()))
        reader_data = read(READER / Path(rel.as_posix()))
        if (
            len(target_data) != expected_bytes
            or sha256_bytes(target_data) != expected_sha256
            or reader_data != target_data
        ):
            fail(f"target-only asset identity or reader copy differs: {rel}")
        try:
            ET.fromstring(target_data)
        except ET.ParseError as exc:
            fail(f"target-only SVG is not well-formed XML: {rel}: {exc}")
        results.append(
            {
                "path": rel.as_posix(),
                "bytes": len(target_data),
                "sha256": sha256_bytes(target_data),
                "reader_target_byte_identical": True,
                "xml_parse": "pass",
            }
        )
    return results


def check_mathjax_runtime() -> dict[str, Any]:
    expected_runtime, authority_record = build_pipeline._runtime_payload()
    runtime_path = READER / Path(build_pipeline.RUNTIME_READER_PATH.as_posix())
    runtime_data = read(runtime_path)
    if runtime_data != expected_runtime:
        fail("reader MathJax boldsymbol runtime differs from the pinned official bytes")
    bundle_path = READER / "MathJax" / "tex-svg.js"
    bundle_data = read(bundle_path)
    if b'"[tex]/boldsymbol"' not in bundle_data:
        fail("MathJax bundle no longer declares the local boldsymbol autoload component")
    script_pages: list[str] = []
    for rel in PAIRS:
        page = READER / Path(rel.as_posix())
        parsed = soup(read(page), f"mathjax-runtime:{rel}")
        for script in parsed.find_all("script", src=True):
            target, fragment = _local_target(page, str(script["src"]))
            if target == bundle_path.resolve():
                if fragment:
                    fail(f"MathJax script reference unexpectedly has a fragment: {rel}")
                script_pages.append(rel.as_posix())
    expected_script_pages = [rel.as_posix() for rel in PAIRS if rel.name != "index.html"]
    if len(expected_script_pages) != 25:
        fail(f"non-index MathJax page census differs: {len(expected_script_pages)}")
    if script_pages != expected_script_pages:
        fail(f"MathJax bundle reference pages changed: {script_pages}")
    return {
        "reader_relative_path": build_pipeline.RUNTIME_READER_PATH.as_posix(),
        "bytes": len(runtime_data),
        "sha256": sha256_bytes(runtime_data),
        "official_tag": authority_record["tag"],
        "official_commit": authority_record["commit"],
        "git_blob_sha1": authority_record["git_blob_sha1"],
        "script_page_references": len(script_pages),
        "script_pages": script_pages,
        "runtime_file_count": 1,
    }


def check_readable_reflow() -> dict[str, Any]:
    rel = PurePosixPath("random/Screen.css")
    authority_data = read(AUTHORITY / Path(rel.as_posix()))
    reader_data = read(READER / Path(rel.as_posix()))
    expected = authority_data + build_pipeline.READABLE_REFLOW_CSS
    if reader_data != expected:
        fail("reader Screen.css is not the exact authority bytes plus readable-layout appendix")
    css = build_pipeline.READABLE_REFLOW_CSS.decode("utf-8")
    required = (
        "O006 id-ID readable layout v3",
        "min-width: 801px",
        "max-width: 72rem",
        "margin: 1rem auto",
        "max-width: 800px",
        "margin: 0.75rem",
        "table {",
        'mjx-container[display="true"]',
        'mjx-assistive-mml[display="block"]',
        "clip-path: inset(50%)",
        "overflow-x: auto",
    )
    missing = [token for token in required if token not in css]
    if missing:
        fail(f"readable-layout invariant missing from CSS appendix: {missing}")
    return {
        "version": "o006-id-readable-layout-v3",
        "reader_relative_path": rel.as_posix(),
        "authority_bytes": len(authority_data),
        "authority_sha256": sha256_bytes(authority_data),
        "append_bytes": len(build_pipeline.READABLE_REFLOW_CSS),
        "append_sha256": sha256_bytes(build_pipeline.READABLE_REFLOW_CSS),
        "reader_bytes": len(reader_data),
        "reader_sha256": sha256_bytes(reader_data),
        "desktop_min_width_px": 801,
        "desktop_max_width_rem": 72,
        "mobile_max_width_px": 800,
        "mobile_fluid": True,
    }


def expected_qa_receipt(
    build_summary: dict[str, Any],
    results: dict[str, dict[str, Any]],
    reference_counts: dict[str, int],
    target_only_assets: list[dict[str, Any]],
    mathjax_runtime: dict[str, Any],
    readable_reflow: dict[str, Any],
) -> dict[str, Any]:
    build_receipt_data = read(build_pipeline.BUILD_RECEIPT)
    qa_script_data = read(Path(__file__).resolve())
    build_script_data = read(Path(build_pipeline.__file__).resolve())
    counts = {
        "translated_pages": len(results),
        "source_elements": sum(int(result["elements"]) for result in results.values()),
        "target_core_elements": sum(
            int(result["target_core_elements"]) for result in results.values()
        ),
        "declared_target_element_insertions": sum(
            int(result["declared_target_element_insertions"]) for result in results.values()
        ),
        "math_spans": sum(int(result["math_spans"]) for result in results.values()),
        "math_delta_spans": sum(
            int(result["math_delta_spans"]) for result in results.values()
        ),
        "raw_math_environments": sum(
            int(result["raw_math_environments"]) for result in results.values()
        ),
        "raw_math_delta_environments": sum(
            int(result["raw_math_delta_environments"]) for result in results.values()
        ),
        "raw_script_style_blocks": sum(
            int(result["raw_script_style_blocks"]) for result in results.values()
        ),
        "href_delta_entries": sum(int(result["href_delta_entries"]) for result in results.values()),
        "href_delta_occurrences": sum(
            int(result["href_delta_occurrences"]) for result in results.values()
        ),
        "href_pair_occurrences": sum(
            int(result["href_pair_occurrences"]) for result in results.values()
        ),
        "occurrence_specific_href_deltas": sum(
            int(result["occurrence_specific_href_deltas"]) for result in results.values()
        ),
        "transport_hardening_deltas": len(build_pipeline.TRANSPORT_HARDENING),
        "controlled_filename_case_corrections": len(CORRECTION_DELTAS),
        "bounded_text_correction_categories": len(build_pipeline.BOUNDED_TEXT_CORRECTIONS),
        "protected_math_correction_categories": len(build_pipeline.PROTECTED_MATH_CORRECTIONS),
        "protected_math_replacements": sum(
            int(result["protected_math_replacements"]) for result in results.values()
        ),
        "math_text_localization_categories": len(build_pipeline.MATH_TEXT_LOCALIZATIONS),
        "math_text_localization_replacements": sum(
            int(result["math_text_localization_replacements"]) for result in results.values()
        ),
        "readable_layout_css_appends": 1,
        "mathjax_runtime_files": int(mathjax_runtime["runtime_file_count"]),
        "target_only_assets": len(target_only_assets),
        "units": sum(int(result["units"]) for result in results.values()),
        "details": sum(int(result["details"]) for result in results.values()),
        "ids": sum(int(result["ids"]) for result in results.values()),
        "reader_files": int(build_summary["file_count"]),
        "reader_bytes": int(build_summary["total_bytes"]),
        **reference_counts,
    }
    return {
        "schema": "o006.random.complete-29-reader-qa.v2",
        "translation_ledger": {
            "path": TRANSLATION_LEDGER.relative_to(ROOT).as_posix(),
            "bytes": len(read(TRANSLATION_LEDGER)),
            "sha256": sha256_bytes(read(TRANSLATION_LEDGER)),
            "rows": len(PAIRS),
            "complete_sequence": "1-29",
        },
        "build": {
            "receipt_path": build_pipeline.BUILD_RECEIPT.relative_to(ROOT).as_posix(),
            "receipt_bytes": len(build_receipt_data),
            "receipt_sha256": sha256_bytes(build_receipt_data),
            "reader_manifest_sha256": build_summary["manifest_sha256"],
            "reader_file_count": build_summary["file_count"],
            "reader_total_bytes": build_summary["total_bytes"],
        },
        "scripts": {
            "build": {
                "path": Path(build_pipeline.__file__).resolve().relative_to(ROOT).as_posix(),
                "bytes": len(build_script_data),
                "sha256": sha256_bytes(build_script_data),
            },
            "qa": {
                "path": Path(__file__).resolve().relative_to(ROOT).as_posix(),
                "bytes": len(qa_script_data),
                "sha256": sha256_bytes(qa_script_data),
            },
        },
        "transport_hardening": list(build_pipeline.TRANSPORT_HARDENING),
        "bounded_text_corrections": list(build_pipeline.BOUNDED_TEXT_CORRECTIONS),
        "protected_math_corrections": list(build_pipeline.PROTECTED_MATH_CORRECTIONS),
        "math_text_localizations": list(build_pipeline.MATH_TEXT_LOCALIZATIONS),
        "target_only_assets": target_only_assets,
        "mathjax_runtime": mathjax_runtime,
        "readable_reflow": readable_reflow,
        "results": results,
        "pass_counts": counts,
    }


def run(*, check_only: bool = False) -> dict[str, Any]:
    validate_allowlist()
    ledger_rows = check_translation_ledger()
    if tuple(ledger_rows) != PAIRS:
        fail("validated translation-ledger order differs from the exact 29-page corpus")
    build_summary = build_pipeline.check(verbose=False)
    results = {rel.as_posix(): compare_pair(rel) for rel in PAIRS}
    intro = results["random/sample/Introduction.html"]
    if intro["units"] != 22 or intro["details"] != 16:
        fail(f"Introduction census changed: {intro}")
    mean = results["random/sample/Mean.html"]
    if mean["units"] != 26 or mean["details"] != 23 or mean["math_spans"] != 365:
        fail(f"Mean census changed: {mean}")
    lln = results["random/sample/LLN.html"]
    if (
        lln["elements"] != 305
        or lln["hierarchy_sha256"]
        != "5c0d5dbd8f5ce20bd12602452d97e7e74779ee36a0186126919674afc4789a07"
        or lln["raw_script_style_blocks"] != 3
        or lln["units"] != 21
        or lln["details"] != 13
        or lln["math_spans"] != 268
        or lln["ids"] != 33
    ):
        fail(f"LLN census changed: {lln}")
    clt = results["random/sample/CLT.html"]
    if (
        clt["elements"] != 424
        or clt["hierarchy_sha256"]
        != "911fcd5705e0e358fb92492b30dea1d53265df24da8d86bf68b10a7f3d56c870"
        or clt["raw_script_style_blocks"] != 3
        or clt["units"] != 38
        or clt["details"] != 21
        or clt["math_spans"] != 394
        or clt["ids"] != 56
    ):
        fail(f"CLT census changed: {clt}")
    variance = results["random/sample/Variance.html"]
    if (
        variance["elements"] != 827
        or variance["hierarchy_sha256"]
        != "1557ceb7383c4bd50eeda2e0b25aa2a98f91fb3dbc5d65dd4ee660c33e1c85b2"
        or variance["raw_script_style_blocks"] != 3
        or variance["units"] != 47
        or variance["details"] != 39
        or variance["math_spans"] != 583
        or variance["ids"] != 64
    ):
        fail(f"Variance census changed: {variance}")
    order_statistics = results["random/sample/OrderStatistics.html"]
    if (
        order_statistics["elements"] != 846
        or order_statistics["hierarchy_sha256"]
        != "defd30f9442dfee7bcfde3f71e15567a96bce8c91132b75240cb23f2c2adc76c"
        or order_statistics["raw_script_style_blocks"] != 4
        or order_statistics["units"] != 51
        or order_statistics["details"] != 34
        or order_statistics["math_spans"] != 569
        or order_statistics["ids"] != 73
    ):
        fail(f"OrderStatistics census changed: {order_statistics}")
    covariance = results["random/sample/Covariance.html"]
    if (
        covariance["elements"] != 906
        or covariance["hierarchy_sha256"]
        != "7ebbc4e8dbc4a99c4baf6358cffce07bedc43b1c01a6b42b8312c9899deaaaea"
        or covariance["raw_script_style_blocks"] != 3
        or covariance["units"] != 58
        or covariance["details"] != 34
        or covariance["math_spans"] != 795
        or covariance["ids"] != 80
    ):
        fail(f"Covariance census changed: {covariance}")
    normal = results["random/sample/Normal.html"]
    if (
        normal["elements"] != 380
        or normal["hierarchy_sha256"]
        != "bdeb23615d43a439d714d09c6dd514747d42e400b5f01db48cd8ad9bccef2a9f"
        or normal["raw_script_style_blocks"] != 3
        or normal["units"] != 29
        or normal["details"] != 21
        or normal["math_spans"] != 380
        or normal["ids"] != 44
    ):
        fail(f"Normal census changed: {normal}")
    point_index = results["random/point/index.html"]
    if (
        point_index["elements"] != 155
        or point_index["hierarchy_sha256"]
        != "6b6d12100e8f69215ad341e2edb91332b75b38265422cd81ac250fe4aaa2fed0"
        or point_index["raw_script_style_blocks"] != 1
        or point_index["units"] != 0
        or point_index["details"] != 0
        or point_index["math_spans"] != 0
        or point_index["ids"] != 6
    ):
        fail(f"point index census changed: {point_index}")
    moments = results["random/point/Moments.html"]
    if (
        moments["elements"] != 440
        or moments["hierarchy_sha256"]
        != "8852c8962c89ef48248ba8c192af3a19d7744869de6a82c625c5280100a1bf90"
        or moments["raw_script_style_blocks"] != 3
        or moments["units"] != 37
        or moments["details"] != 29
        or moments["math_spans"] != 649
        or moments["ids"] != 54
        or moments["href_delta_entries"] != 33
        or moments["href_delta_occurrences"] != 40
        or moments["protected_math_replacements"] != 12
    ):
        fail(f"Moments census changed: {moments}")
    likelihood = results["random/point/Likelihood.html"]
    if (
        likelihood["elements"] != 397
        or likelihood["hierarchy_sha256"]
        != "a18199fa53fb52e2c12f46fa5fc93ab06b5d76cda4f3a4d127461901dc9f153a"
        or likelihood["raw_script_style_blocks"] != 3
        or likelihood["units"] != 35
        or likelihood["details"] != 22
        or likelihood["math_spans"] != 589
        or likelihood["ids"] != 53
        or likelihood["href_delta_entries"] != 30
        or likelihood["href_delta_occurrences"] != 34
        or likelihood["protected_math_replacements"] != 36
        or likelihood["math_text_localization_replacements"] != 1
    ):
        fail(f"Likelihood census changed: {likelihood}")
    bayes = results["random/point/Bayes.html"]
    if (
        bayes["elements"] != 352
        or bayes["hierarchy_sha256"]
        != "84a3f8750b133d3dd77e245ebc56e7a65501e967f038b20f36e1783fa0eb5dca"
        or bayes["raw_script_style_blocks"] != 3
        or bayes["raw_math_environments"] != 8
        or bayes["units"] != 31
        or bayes["details"] != 23
        or bayes["math_spans"] != 625
        or bayes["ids"] != 46
        or bayes["href_delta_entries"] != 30
        or bayes["href_delta_occurrences"] != 36
        or bayes["protected_math_replacements"] != 17
    ):
        fail(f"Bayes census changed: {bayes}")
    unbiased = results["random/point/Unbiased.html"]
    if (
        unbiased["source_bytes"] != 28635
        or unbiased["source_sha256"]
        != "0d9765c5c7b5b8a54b29fc45c3a435d20e2a9200e027609658345087dedcd531"
        or unbiased["elements"] != 306
        or unbiased["hierarchy_sha256"]
        != "1e14318d47c2a1c0c10f92651073868420f2acb258a06e4edf5158fe489ce9b1"
        or unbiased["raw_script_style_blocks"] != 3
        or unbiased["raw_math_environments"] != 4
        or unbiased["raw_math_sha256"]
        != "7df75b42a511a5178054596d5ecfcd8dce66f20013732a9e1c114fd2d3cabc5b"
        or unbiased["units"] != 38
        or unbiased["details"] != 10
        or unbiased["math_spans"] != 243
        or unbiased["ids"] != 52
        or unbiased["href_delta_entries"] != 33
        or unbiased["href_delta_occurrences"] != 34
        or unbiased["occurrence_specific_href_deltas"] != 9
        or unbiased["protected_math_replacements"] != 6
        or unbiased["math_text_localization_replacements"] != 0
    ):
        fail(f"Unbiased census changed: {unbiased}")
    reference_counts = check_reader_references()
    target_only_assets = check_target_only_assets()
    mathjax_runtime = check_mathjax_runtime()
    readable_reflow = check_readable_reflow()
    receipt = expected_qa_receipt(
        build_summary,
        results,
        reference_counts,
        target_only_assets,
        mathjax_runtime,
        readable_reflow,
    )
    receipt_data = build_pipeline.canonical_json_bytes(receipt)
    if check_only:
        actual = build_pipeline.read_regular(QA_RECEIPT, reject_hardlinks=True)
        if actual != receipt_data:
            fail("first-unit QA receipt is stale or noncanonical")
    else:
        build_pipeline.make_directory(QA_RECEIPT.parent)
        build_pipeline.write_regular(QA_RECEIPT, receipt_data)
    actual = build_pipeline.read_regular(QA_RECEIPT, reject_hardlinks=True)
    if actual != receipt_data:
        fail("first-unit QA receipt replay mismatch")
    counts = receipt["pass_counts"]
    print(
        f"PASS QA: {counts['translated_pages']} translated pages / "
        f"{counts['reader_bytes']} reader bytes / {counts['units']} units / "
        f"{counts['details']} details / {counts.get('local_refs', 0)} local refs / "
        f"{counts.get('fragments', 0)} fragments / receipt {sha256_bytes(actual)}"
    )
    return {
        "qa_receipt_bytes": len(actual),
        "qa_receipt_sha256": sha256_bytes(actual),
        "pass_counts": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    run(check_only=args.check_only)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
