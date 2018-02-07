#!/usr/bin/env python3
# Copyright (c) 2017 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

from random import randint
from test_framework.test_framework import BitcoinTestFramework
from test_framework.util import assert_equal

class ExampleTest(BitcoinTestFramework):

    def set_test_params(self):
        self.num_nodes = 3
        self.setup_clean_chain = True
        self.supports_cli = True
        self._to_mine = 100

    def run_test(self):
        self.log.info("=============Start=============")

        # Mine some blocks
        block_cnt = self.nodes[0].getblockcount()
        assert_equal(block_cnt, 0)
        self.nodes[0].generate(1)
        self.nodes[1].generate(101)
        self.sync_all()
        assert_equal(self.nodes[0].getbalance(), 50)
        assert_equal(self.nodes[1].getbalance(), 50)

        # Sent some coins to node2
        addr_node2 = self.nodes[2].getnewaddress()
        txid = self.nodes[1].sendtoaddress(addr_node2, 25, "", "", True)
        self.nodes[1].generate(1)
        self.sync_all()
        unspent = self.nodes[2].listunspent()
        assert_equal(len(unspent), 1)
        assert_equal(unspent[0]['txid'], txid)

        # Check fee
        fee = self.nodes[1].gettransaction(txid)['fee']
        assert_equal(unspent[0]['amount'], 25+fee)
        assert_equal(self.nodes[1].getbalance(), 75)

        # Lets explode the mempool:
        self.log.info("Explode mempool :)....")
        for i in range(10000):
            node = randint(1,2)
            txid = self.nodes[1].sendtoaddress(self.nodes[node].getnewaddress(), .001, "", "", True)
            self.sync_all()
            self.log.info(self.nodes[0].estimatesmartfee(2))
            self.log.info(self.nodes[0].getmempoolinfo())

        self.log.info("=============Stop==============")

if __name__ == '__main__':
    ExampleTest().main()
