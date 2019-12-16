socket_to_sc = {}

# 已建立的安全通道列表
# 不一定是登入状态，只是连接
scs = []

def remove_sc_from_socket_mapping(sc):
    if sc in scs:
        scs.remove(sc)

    if sc.socket in socket_to_sc:
        del socket_to_sc[sc.socket]
