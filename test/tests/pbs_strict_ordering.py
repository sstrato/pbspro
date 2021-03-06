# coding: utf-8

# Copyright (C) 1994-2016 Altair Engineering, Inc.
# For more information, contact Altair at www.altair.com.
#
# This file is part of the PBS Professional ("PBS Pro") software.
#
# Open Source License Information:
#
# PBS Pro is free software. You can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# PBS Pro is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Commercial License Information:
#
# The PBS Pro software is licensed under the terms of the GNU Affero General
# Public License agreement ("AGPL"), except where a separate commercial license
# agreement for PBS Pro version 14 or later has been executed in writing with Altair.
#
# Altair’s dual-license business model allows companies, individuals, and
# organizations to create proprietary derivative works of PBS Pro and distribute
# them - whether embedded or bundled with other software - under a commercial
# license agreement.
#
# Use of Altair’s trademarks, including but not limited to "PBS™",
# "PBS Professional®", and "PBS Pro™" and Altair’s logos is subject to Altair's
# trademark licensing policies.

import os
import string
import time

from ptl.utils.pbs_testsuite import *


class Test_strict_ordering_without_backfill(PBSTestSuite):

    """
    Test strict ordering when backfilling is truned off
    """
    @timeout(1800)
    def test_t1(self):

        a = {'resources_available.ncpus': 4}
        self.server.create_vnodes('vn', a, 1, self.mom, usenatvnode=True)

        rv = self.scheduler.set_sched_config(
            {'round_robin': 'false all', 'by_queue': 'false prime', 
	     'by_queue': 'false non_prime', 'strict_ordering': 'true all', 
	     'help_starving_jobs': 'false all'})
        self.assertTrue(rv)

        a = {'backfill_depth': 0}
        rv = self.server.manager(MGR_CMD_SET, SERVER, a, expect=True)
        self.assertTrue(rv)

        j1 = Job(TEST_USER)
        a = {'Resource_List.select': '1:ncpus=2',
             'Resource_List.walltime': 9999}
        j1.set_sleep_time(9999)
        j1.set_attributes(a)
        j1 = self.server.submit(j1)

        j2 = Job(TEST_USER)
        a = {'Resource_List.select': '1:ncpus=3',
             'Resource_List.walltime': 9999}
        j2.set_sleep_time(9999)
        j2.set_attributes(a)
        j2 = self.server.submit(j2)

        j3 = Job(TEST_USER)
        a = {'Resource_List.select': '1:ncpus=2',
             'Resource_List.walltime': 9999}
        j3.set_sleep_time(9999)
        j3.set_attributes(a)
        j3 = self.server.submit(j3)
	try:
	    rv = self.server.expect(JOB, {'comment': 'Not Running: Job would break strict sorted order'}, id=j3,
                           offset=2, max_attempts=2, interval=2)
	except PtlExpectError, e:
	    self.assertTrue(False)
