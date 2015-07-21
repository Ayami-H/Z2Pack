#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author:  Dominik Gresch <greschd@gmx.ch>
# Date:    15.10.2014 10:22:43 CEST
# File:    tb_example.py

from common import *

import os
import copy
import types
import shutil

class TbTrsExampleTestCase(BuildDirTestCase):

    def createH(self, t1, t2):

        builder = z2pack.em.tb.Builder()

        # create the two atoms
        builder.add_atom([1], [0, 0, 0], 1)
        builder.add_atom([-1], [0.5, 0.5, 0], 0)

        # add hopping between different atoms
        builder.add_hopping(((0, 0), (1, 0)),
                           z2pack.em.tb.vectors.combine([0, -1], [0, -1], 0),
                           t1,
                           phase=[1, -1j, 1j, -1])

        # add hopping between neighbouring orbitals of the same type
        builder.add_hopping(((0, 0), (0, 0)),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           t2,
                           phase=[1])
        builder.add_hopping(((1, 0), (1, 0)),
                           z2pack.em.tb.vectors.neighbours([0, 1],
                                                        forward_only=True),
                           -t2,
                           phase=[1])
        self.model = builder.create()
        self.trs_model = self.model.trs()

    # this test may produce false negatives due to small numerical differences
    def test_notrs(self):
        self.createH(0.2, 0.3)
        system = z2pack.em.tb.System(self.model)
        surface = system.surface(lambda kx, ky: [kx, ky, 0])
        surface.wcc_calc(verbose=False, num_strings=20, pickle_file=None)

        # explicitly compare to known results
        self.assertAlmostEqual(surface.chern()['chern'], 1.)

        # compare to old results
        res = {'t_par': [0.0, 0.052631578947368418, 0.10526315789473684, 0.15789473684210525, 0.21052631578947367, 0.26315789473684209, 0.31578947368421051, 0.36842105263157893, 0.42105263157894735, 0.47368421052631576, 0.52631578947368418, 0.57894736842105265, 0.63157894736842102, 0.68421052631578938, 0.73684210526315785, 0.78947368421052633, 0.84210526315789469, 0.89473684210526305, 0.94736842105263153, 1.0], 'wcc': [[0.5], [0.50290547562010501], [0.50632496909432589], [0.5109796888045266], [0.51817971041413013], [0.53083513898799439], [0.55674922240638969], [0.61882939347683608], [0.75263058836445063], [0.9201572438592639], [0.07984275614073584], [0.24736941163554943], [0.38117060652316376], [0.44325077759361031], [0.46916486101200566], [0.48182028958586998], [0.48902031119547335], [0.49367503090567405], [0.49709452437989504], [0.5]], 'lambda_': [array([[-1. -1.11022302e-16j]]), array([[-0.99983337+0.01825463j]]), array([[-0.99921043+0.03973049j]]), array([[-0.99762131+0.06893271j]]), array([[-0.99348324+0.11397825j]]), array([[-0.98129048+0.1925331j]]), array([[-0.93710105+0.34905818j]]), array([[-0.7339838+0.67916697j]]), array([[ 0.01652772+0.99986341j]]), array([[ 0.87678222+0.48088765j]]), array([[ 0.87678222-0.48088765j]]), array([[ 0.01652772-0.99986341j]]), array([[-0.7339838-0.67916697j]]), array([[-0.93710105-0.34905818j]]), array([[-0.98129048-0.1925331j]]), array([[-0.99348324-0.11397825j]]), array([[-0.99762131-0.06893271j]]), array([[-0.99921043-0.03973049j]]), array([[-0.99983337-0.01825463j]]), array([[-1. +2.77555756e-16j]])], 'kpt': [[0.0, 0.0, 0], [0.052631578947368418, 0.0, 0], [0.10526315789473684, 0.0, 0], [0.15789473684210525, 0.0, 0], [0.21052631578947367, 0.0, 0], [0.26315789473684209, 0.0, 0], [0.31578947368421051, 0.0, 0], [0.36842105263157893, 0.0, 0], [0.42105263157894735, 0.0, 0], [0.47368421052631576, 0.0, 0], [0.52631578947368418, 0.0, 0], [0.57894736842105265, 0.0, 0], [0.63157894736842102, 0.0, 0], [0.68421052631578938, 0.0, 0], [0.73684210526315785, 0.0, 0], [0.78947368421052633, 0.0, 0], [0.84210526315789469, 0.0, 0], [0.89473684210526305, 0.0, 0], [0.94736842105263153, 0.0, 0], [1.0, 0.0, 0]], 'gap': [0.0, 0.0029054756201050136, 0.006324969094325894, 0.010979688804526599, 0.018179710414130135, 0.030835138987994393, 0.056749222406389688, 0.11882939347683608, 0.25263058836445063, 0.42015724385926401, 0.57984275614073588, 0.74736941163554937, 0.8811706065231637, 0.94325077759361031, 0.96916486101200561, 0.98182028958586998, 0.9890203111954734, 0.99367503090567411, 0.99709452437989499, 0.0]}

        self.assertFullAlmostEqual(res, surface.get_res())

    def test_trs(self):
        self.createH(0.2, 0.3)
        trs_system = z2pack.em.tb.System(self.trs_model)
        trs_surface = trs_system.surface(lambda kx, ky: [kx, ky, 0])
        trs_surface.wcc_calc(verbose=False, num_strings=20, pickle_file=None)

        trs_surface_z2 = trs_system.surface(lambda kx, ky: [kx / 2., ky, 0])
        trs_surface_z2.wcc_calc(verbose=False, num_strings=20, pickle_file=None)

        # explicitly compare to known results
        self.assertAlmostEqual(trs_surface.chern()['chern'], 0.)
        self.assertEqual(trs_surface_z2.z2(), 1)

        # compare to old results
        trs_res = {'t_par': [0.0, 0.052631578947368418, 0.10526315789473684, 0.15789473684210525, 0.21052631578947367, 0.26315789473684209, 0.31578947368421051, 0.36842105263157893, 0.42105263157894735, 0.44736842105263153, 0.47368421052631576, 0.52631578947368418, 0.55263157894736836, 0.57894736842105265, 0.63157894736842102, 0.68421052631578938, 0.73684210526315785, 0.78947368421052633, 0.84210526315789469, 0.89473684210526305, 0.94736842105263153, 1.0], 'wcc': [[0.5, 0.5], [0.49709452437989504, 0.50290547562010501], [0.49367503090567405, 0.50632496909432589], [0.48902031119547346, 0.5109796888045266], [0.48182028958586998, 0.51817971041413013], [0.46916486101200566, 0.53083513898799439], [0.44325077759361031, 0.55674922240638969], [0.38117060652316404, 0.61882939347683608], [0.24736941163554962, 0.75263058836445063], [0.16289846536332953, 0.83710153463667059], [0.07984275614073616, 0.9201572438592639], [0.07984275614073584, 0.92015724385926423], [0.162898465363329, 0.83710153463667103], [0.24736941163554943, 0.75263058836445063], [0.38117060652316376, 0.6188293934768363], [0.44325077759361031, 0.55674922240638991], [0.46916486101200566, 0.53083513898799439], [0.48182028958586998, 0.51817971041413013], [0.48902031119547335, 0.51097968880452682], [0.49367503090567405, 0.50632496909432589], [0.49709452437989504, 0.50290547562010501], [0.5, 0.5]], 'lambda_': [array([[-1. -1.11022302e-16j,  0. +0.00000000e+00j],
       [ 0. +0.00000000e+00j, -1. +2.22044605e-16j]]), array([[-0.99983337+0.01825463j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99983337-0.01825463j]]), array([[-0.99921043+0.03973049j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99921043-0.03973049j]]), array([[-0.99762131+0.06893271j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99762131-0.06893271j]]), array([[-0.99348324+0.11397825j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99348324-0.11397825j]]), array([[-0.98129048+0.1925331j,  0.00000000+0.j       ],
       [ 0.00000000+0.j       , -0.98129048-0.1925331j]]), array([[-0.93710105+0.34905818j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.93710105-0.34905818j]]), array([[-0.7339838+0.67916697j, -0.0000000+0.j        ],
       [ 0.0000000+0.j        , -0.7339838-0.67916697j]]), array([[ 0.01652772+0.99986341j, -0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.01652772-0.99986341j]]), array([[ 0.52036223+0.85394563j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.52036223-0.85394563j]]), array([[ 0.87678222+0.48088765j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.87678222-0.48088765j]]), array([[ 0.87678222-0.48088765j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.87678222+0.48088765j]]), array([[ 0.52036223-0.85394563j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.52036223+0.85394563j]]), array([[ 0.01652772-0.99986341j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.01652772+0.99986341j]]), array([[-0.7339838-0.67916697j,  0.0000000+0.j        ],
       [ 0.0000000+0.j        , -0.7339838+0.67916697j]]), array([[-0.93710105-0.34905818j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.93710105+0.34905818j]]), array([[-0.98129048-0.1925331j,  0.00000000+0.j       ],
       [ 0.00000000+0.j       , -0.98129048+0.1925331j]]), array([[-0.99348324-0.11397825j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99348324+0.11397825j]]), array([[-0.99762131-0.06893271j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99762131+0.06893271j]]), array([[-0.99921043-0.03973049j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99921043+0.03973049j]]), array([[-0.99983337-0.01825463j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99983337+0.01825463j]]), array([[-1. +2.77555756e-16j,  0. +0.00000000e+00j],
       [ 0. +0.00000000e+00j, -1. +0.00000000e+00j]])], 'kpt': [[0.0, 0.0, 0], [0.052631578947368418, 0.0, 0], [0.10526315789473684, 0.0, 0], [0.15789473684210525, 0.0, 0], [0.21052631578947367, 0.0, 0], [0.26315789473684209, 0.0, 0], [0.31578947368421051, 0.0, 0], [0.36842105263157893, 0.0, 0], [0.42105263157894735, 0.0, 0], [0.44736842105263153, 0.0, 0], [0.47368421052631576, 0.0, 0], [0.52631578947368418, 0.0, 0], [0.55263157894736836, 0.0, 0], [0.57894736842105265, 0.0, 0], [0.63157894736842102, 0.0, 0], [0.68421052631578938, 0.0, 0], [0.73684210526315785, 0.0, 0], [0.78947368421052633, 0.0, 0], [0.84210526315789469, 0.0, 0], [0.89473684210526305, 0.0, 0], [0.94736842105263153, 0.0, 0], [1.0, 0.0, 0]], 'gap': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.50000000000000011, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]}
        trs_res_z2 = {'t_par': [0.0, 0.052631578947368418, 0.10526315789473684, 0.15789473684210525, 0.21052631578947367, 0.26315789473684209, 0.31578947368421051, 0.36842105263157893, 0.42105263157894735, 0.47368421052631576, 0.52631578947368418, 0.57894736842105265, 0.63157894736842102, 0.68421052631578938, 0.73684210526315785, 0.78947368421052633, 0.84210526315789469, 0.89473684210526305, 0.94736842105263153, 1.0], 'wcc': [[0.5, 0.5], [0.4985772864558789, 0.50142271354412116], [0.49709452437989504, 0.50290547562010501], [0.49548621602752185, 0.50451378397247815], [0.49367503090567405, 0.50632496909432589], [0.49156327455047089, 0.50843672544952923], [0.48902031119547346, 0.5109796888045266], [0.48586262147153575, 0.51413737852846442], [0.48182028958586998, 0.51817971041413013], [0.47647779570687199, 0.52352220429312823], [0.46916486101200566, 0.53083513898799439], [0.4587495497891878, 0.54125045021081231], [0.44325077759361031, 0.55674922240638969], [0.41920395918109998, 0.58079604081890002], [0.38117060652316404, 0.61882939347683608], [0.32357716638788775, 0.67642283361211231], [0.24736941163554962, 0.75263058836445063], [0.16289846536332953, 0.83710153463667059], [0.07984275614073616, 0.9201572438592639], [6.1844118806235042e-17, 1.0]], 'lambda_': [array([[-1. -1.11022302e-16j,  0. +0.00000000e+00j],
       [ 0. +0.00000000e+00j, -1. +2.22044605e-16j]]), array([[-0.99996005+0.00893905j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99996005-0.00893905j]]), array([[-0.99983337+0.01825463j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99983337-0.01825463j]]), array([[-0.99959786+0.02835714j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99959786-0.02835714j]]), array([[-0.99921043+0.03973049j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99921043-0.03973049j]]), array([[-0.99859532+0.05298469j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99859532-0.05298469j]]), array([[-0.99762131+0.06893271j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99762131-0.06893271j]]), array([[-0.99605741+0.088711j,  0.00000000+0.j      ],
       [ 0.00000000+0.j      , -0.99605741-0.088711j]]), array([[-0.99348324+0.11397825j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.99348324-0.11397825j]]), array([[-0.98909828+0.14725691j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.98909828-0.14725691j]]), array([[-0.98129048+0.1925331j,  0.00000000+0.j       ],
       [ 0.00000000+0.j       , -0.98129048-0.1925331j]]), array([[-0.96659938+0.25629211j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.96659938-0.25629211j]]), array([[-0.93710105+0.34905818j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.93710105-0.34905818j]]), array([[-0.87388616+0.48613063j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.87388616-0.48613063j]]), array([[-0.7339838+0.67916697j, -0.0000000+0.j        ],
       [ 0.0000000+0.j        , -0.7339838-0.67916697j]]), array([[-0.44600693+0.89502951j, -0.00000000+0.j        ],
       [ 0.00000000+0.j        , -0.44600693-0.89502951j]]), array([[ 0.01652772+0.99986341j, -0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.01652772-0.99986341j]]), array([[ 0.52036223+0.85394563j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.52036223-0.85394563j]]), array([[ 0.87678222+0.48088765j,  0.00000000+0.j        ],
       [ 0.00000000+0.j        ,  0.87678222-0.48088765j]]), array([[ 1. -3.88578059e-16j,  0. +0.00000000e+00j],
       [ 0. +0.00000000e+00j,  1. +2.22044605e-16j]])], 'kpt': [[0.0, 0.0, 0], [0.026315789473684209, 0.0, 0], [0.052631578947368418, 0.0, 0], [0.078947368421052627, 0.0, 0], [0.10526315789473684, 0.0, 0], [0.13157894736842105, 0.0, 0], [0.15789473684210525, 0.0, 0], [0.18421052631578946, 0.0, 0], [0.21052631578947367, 0.0, 0], [0.23684210526315788, 0.0, 0], [0.26315789473684209, 0.0, 0], [0.28947368421052633, 0.0, 0], [0.31578947368421051, 0.0, 0], [0.34210526315789469, 0.0, 0], [0.36842105263157893, 0.0, 0], [0.39473684210526316, 0.0, 0], [0.42105263157894735, 0.0, 0], [0.44736842105263153, 0.0, 0], [0.47368421052631576, 0.0, 0], [0.5, 0.0, 0]], 'gap': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.50000000000000011, 0.5, 0.5, 0.5]}

        self.assertFullAlmostEqual(trs_res, trs_surface.get_res())
        self.assertFullAlmostEqual(trs_res_z2, trs_surface_z2.get_res())

    def test_trs_inplace(self):
        self.createH(0.2, 0.3)
        # create a second TRS model by in-place replacing
        model2 = copy.deepcopy(self.model)
        model2.trs(in_place=True)
        system0 = z2pack.em.tb.System(self.trs_model)
        surface0 = system0.surface(lambda kx, ky: [kx, ky, 0])
        surface0.wcc_calc(verbose=False, num_strings=20, pickle_file=None)
        system1 = z2pack.em.tb.System(model2)
        surface1 = system1.surface(lambda kx, ky: [kx, ky, 0])
        surface1.wcc_calc(verbose=False, num_strings=20, pickle_file=None)

        self.assertFullAlmostEqual(surface0.get_res(), surface1.get_res())

if __name__ == "__main__":
    unittest.main()
