import nose.tools as nt
from cis_interface.communication.tests import test_CommBase


class TestServerComm(test_CommBase.TestCommBase):
    r"""Tests for ServerComm communication class."""
    def __init__(self, *args, **kwargs):
        super(TestServerComm, self).__init__(*args, **kwargs)
        self.comm = 'ServerComm'
        self.attr_list += ['response_kwargs', 'icomm', 'ocomm']

    @property
    def send_inst_kwargs(self):
        r"""dict: Keyword arguments for send instance."""
        return {'comm': 'ClientComm'}
    
    def test_error_send(self):
        r"""Disabled: Test error on send."""
        pass
        
    def test_error_recv(self):
        r"""Disabled: Test error on recv."""
        pass
        
    def test_invalid_direction(self):
        r"""Disabled: Test of error on incorrect direction."""
        pass
    
    def test_work_comm(self):
        r"""Disabled: Test creating/removing a work comm."""
        pass
        
    def test_eof(self):
        r"""Test send/recv of EOF message."""
        # Forwards
        flag = self.send_instance.send_eof()
        assert(flag)
        flag, msg_recv = self.recv_instance.recv()
        assert(not flag)
        nt.assert_equal(msg_recv, self.send_instance.eof_msg)
        # Assert
        # assert(self.recv_instance.is_closed)

    def test_eof_nolimit(self):
        r"""Test send/recv of EOF message through nolimit."""
        # Forwards
        flag = self.send_instance.send_nolimit_eof()
        assert(flag)
        flag, msg_recv = self.recv_instance.recv_nolimit()
        assert(not flag)
        nt.assert_equal(msg_recv, self.send_instance.eof_msg)
        # Assert
        # assert(self.recv_instance.is_closed)

    def test_call(self):
        r"""Test RPC call."""
        self.send_instance.sched_task(0.0, self.send_instance.rpcCall,
                                      args=[self.msg_short], store_output=True)
        flag, msg_recv = self.recv_instance.rpcRecv(timeout=self.timeout)
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_short)
        flag = self.recv_instance.rpcSend(msg_recv)
        assert(flag)
        T = self.recv_instance.start_timeout()
        while (not T.is_out) and (self.send_instance.sched_out is None):
            self.recv_instance.sleep()
        self.recv_instance.stop_timeout()
        flag, msg_recv = self.send_instance.sched_out
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_short)

    def test_call_alias(self):
        r"""Test RPC call aliases."""
        # self.send_instance.sched_task(0.0, self.send_instance.rpcSend,
        #                               args=[self.msg_short], store_output=True)
        flag = self.send_instance.rpcSend(self.msg_short)
        assert(flag)
        flag, msg_recv = self.recv_instance.rpcRecv(timeout=self.timeout)
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_short)
        flag = self.recv_instance.rpcSend(msg_recv)
        assert(flag)
        flag, msg_recv = self.send_instance.rpcRecv(timeout=self.timeout)
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_short)

    def test_call_nolimit(self):
        r"""Test RPC nolimit call."""
        self.send_instance.sched_task(0.0, self.send_instance.call_nolimit,
                                      args=[self.msg_long], store_output=True)
        flag, msg_recv = self.recv_instance.recv_nolimit(timeout=self.timeout)
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_long)
        flag = self.recv_instance.send_nolimit(msg_recv)
        assert(flag)
        T = self.recv_instance.start_timeout()
        while (not T.is_out) and (self.send_instance.sched_out is None):
            self.recv_instance.sleep()
        self.recv_instance.stop_timeout()
        flag, msg_recv = self.send_instance.sched_out
        assert(flag)
        nt.assert_equal(msg_recv, self.msg_long)

    # # This dosn't work for comms that are uni-directional
    # def test_purge_recv(self):
    #     r"""Test purging messages from the client comm."""
    #     # Purge send while open
    #     if self.comm != 'CommBase':
    #         flag = self.send_instance.send(self.msg_short)
    #         assert(flag)
    #         T = self.recv_instance.start_timeout()
    #         while (not T.is_out) and (self.recv_instance.n_msg == 0):  # pragma: debug
    #             self.recv_instance.sleep()
    #         self.recv_instance.stop_timeout()
    #         nt.assert_equal(self.recv_instance.n_msg, 1)
    #     self.send_instance.purge()
    #     nt.assert_equal(self.send_instance.n_msg, 0)
    #     nt.assert_equal(self.recv_instance.n_msg, 0)
    #     # Purge send while closed
    #     self.send_instance.close()
    #     self.send_instance.purge()
