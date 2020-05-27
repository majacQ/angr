
import os

import nose.tools

import angr

test_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', '..', 'binaries', 'tests')

def test_libc_x86():

    p = angr.Project(os.path.join(test_location, "i386", "libc-2.27-3ubuntu1.so.6"), auto_load_libs=True)
    dl_addr = p.loader.find_symbol('_dl_addr').rebased_addr
    cfg = p.analyses.CFGFast(regions=[(dl_addr, dl_addr + 4096)])
    func = cfg.functions['_dl_addr']

    rtld_global_sym = p.loader.find_symbol('_rtld_global')
    assert rtld_global_sym is not None
    _rtld_global_addr = rtld_global_sym.rebased_addr

    base_addr = 0x998f000
    state = p.factory.blank_state()
    for addr in range(0, 0 + 0x1000, p.arch.bytes):
        state.memory.store(_rtld_global_addr + addr, base_addr + addr, size=p.arch.bytes,
                           endness=p.arch.memory_endness)

    prop = p.analyses.Propagator(func=func, base_state=state)
    # import pprint
    # pprint.pprint(prop.replacements)
    nose.tools.assert_greater(len(prop.replacements), 0)


def test_lwip_udpecho_bm():
    bin_path = os.path.join(test_location, "armel", "lwip_udpecho_bm.elf")
    p = angr.Project(bin_path, auto_load_libs=False)
    cfg = p.analyses.CFG(data_references=True)

    func = cfg.functions[0x23c9]
    state = p.factory.blank_state()
    prop = p.analyses.Propagator(func=func, base_state=state)

    nose.tools.assert_greater(len(prop.replacements), 0)

def test_register_points():
    bin_path = os.path.join(test_location, "armel", "lol_prop")
    p = angr.Project(bin_path, auto_load_libs=False)
    cfg = p.analyses.CFG(data_references=True)
    f = cfg.functions[p.entry]
    state = p.factory.blank_state()
    prop = p.analyses.Propagator(func=f, base_state=state)
    nose.tools.assert_equal(prop.get_register_at_block(p.entry, 'r0'), 0x40001234)

def test_initial_regs():
    bin_path = os.path.join(test_location, "armel", "lol_prop")
    p = angr.Project(bin_path, auto_load_libs=False)
    cfg = p.analyses.CFG(data_references=True)
    f = cfg.functions[p.entry]
    state = p.factory.blank_state()
    prop = p.analyses.Propagator(func=f, base_state=state, initial_registers={'r1': 0xface})
    nose.tools.assert_equal(prop.get_register_at_block(p.entry, 'r1'), 0xbeef + 0xface)


if __name__ == "__main__":
    test_libc_x86()
    test_lwip_udpecho_bm()
    test_register_points()
    test_initial_regs()
