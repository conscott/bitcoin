#!/usr/bin/env python3
# Copyright (c) 2015-2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test making and accepting various transaction sizes."""

from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import *
from test_framework.mininode import COIN, MAX_BLOCK_BASE_SIZE


class TxSizeTest(BitcoinTestFramework):

    def set_test_params(self):
        self.setup_clean_chain = True
        self.num_nodes = 2

    def create_tx_and_check_size_diff(self, target, fee=None):
        txid = create_tx_with_size(self.nodes[0], target, fee=fee)
        tx = self.nodes[0].getrawtransaction(txid, True)
        diff = tx['vsize'] - target
        self.log.debug("Target %s, Actual %s, diff = %s" % (target, tx['vsize'], diff))
        assert_equal(0, diff)

    def run_test(self):

        self.log.info("Checking too small of size increase...")
        # Base tx size is ~155 byes, should error if only slightly larger because
        # it can't make an extra output less than 13 bytes
        assert_raises(AssertionError, self.create_tx_and_check_size_diff, 160)


        self.log.info("Checking block base size limit...")

        # Should be fine on limit
        self.create_tx_and_check_size_diff(MAX_BLOCK_BASE_SIZE)

        # Should raise exception if 1 byte over
        assert_raises_rpc_error(-26, 'bad-txns-oversize', create_tx_with_size, self.nodes[0], MAX_BLOCK_BASE_SIZE + 1)

        self.log.info("Checking range of sizes...")
        # Test from range 171 - 881,898
        for i in range(64):
            tx_size = 155 + int(2**(4+i*0.25))
            # Pay between 1 - 50 sat/byte
            fee = tx_size / COIN * random.randint(1, 50)
            self.create_tx_and_check_size_diff(tx_size, fee=fee)


if __name__ == '__main__':
    TxSizeTest().main()
