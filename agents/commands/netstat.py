import psutil

def run():
    connections = psutil.net_connections()
    result = []
    for c in connections:
        # Формируем удобочитаемую строку для каждого соединения
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else ""
        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else ""
        status = c.status
        pid = c.pid

        result.append({
            "local_address": laddr,
            "remote_address": raddr,
            "status": status,
            "pid": pid,
        })

    return result
