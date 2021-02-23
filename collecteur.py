""" collecteur
application to collect computer system information

with CPU info
     network counter
     memory use info
     hard disk occupancy rate
     battery level

"""
import time
import mariadb
import psutil


def get_net_io_counters():
    """Get the net I/O counters

      return the net io counters

      Available : bytes send, bytes received, packets send, packets received
    """

    stats_net = psutil.net_io_counters(
        pernic=False,
        nowrap=False,
    )
    my_network_stats = [
        f"bytes send: {get_size(stats_net.bytes_sent)}" + ",",
        f" bytes received: {get_size(stats_net.bytes_recv)}" + ",",
        f" packets send: {get_size(stats_net.packets_sent)}" + ",",
        f" packets received: {get_size(stats_net.packets_recv)}"
    ]
    return "".join(my_network_stats)


#
# define variable for SQL request for network stats
#
bytes_sent = psutil.net_io_counters(pernic=False, nowrap=False, ).bytes_sent
bytes_received = psutil.net_io_counters(pernic=False, nowrap=False, ).bytes_recv
packets_sent = psutil.net_io_counters(pernic=False, nowrap=False, ).packets_sent
packets_received = psutil.net_io_counters(pernic=False, nowrap=False, ).packets_recv


def get_cpu_percent():
    """ get the cpu infos in pourcent

    return the cpu  pourcent stats
    """
    return psutil.cpu_percent(
        interval=None,
        percpu=False,
    )


def get_disk_usage():
    """ get hard drive occupation

    return disk stats

    Available fields : total, used, free, percent
    """

    stats_disk = psutil.disk_usage('/')
    my_disk_stats = [
        f"total: {get_size(stats_disk.total)}" + ",",
        f" used: {get_size(stats_disk.used)}" + ",",
        f" free: {get_size(stats_disk.free)}" + ",",
        f" percent: " + str(stats_disk.percent)
    ]

    return "".join(my_disk_stats)


#
# define variable for SQL request for disk usage
#

total_disk = psutil.disk_usage('/').total
used_disk = psutil.disk_usage('/').used
free_disk = psutil.disk_usage('/').free
percent_disk = psutil.disk_usage('/').percent


def get_memory_usage():
    """  get the virtual memory stats

    return memory stats

    Available fields : total, available, percent, used, free
    """
    stats = psutil.virtual_memory()
    my_memory_stats = [
        f"total: {get_size(stats.total)}" + ",",
        f" available: {get_size(stats.available)}" + ",",
        f" percent: " + str(stats.percent) + ",",
        f" used: {get_size(stats.used)}" + ",",
        f" free: {get_size(stats.free)}"
    ]
    return "".join(my_memory_stats)


#
# define variable for SQL request for memory stats
#
total_memory = psutil.virtual_memory().total
available_memory = psutil.virtual_memory().available
percent_memory = psutil.virtual_memory().percent
used_memory = psutil.virtual_memory().used
free_memory = psutil.virtual_memory().free


def get_battery_level():
    """ get somme battery stats

    return battery level

    Available  fields:  percent, secsleft, power_plugged
    """
    stats = psutil.sensors_battery()
    my_battery_stats = [
        str(stats.percent),

    ]
    return "".join(my_battery_stats)


def write_to_file(text):
    """ write text into a file
    args : text
    return : none
    """
    with open("recup_data.txt", "a+") as file:
        file.write(text + "\n")


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


def write_to_db(sqlstatement):
    """Write to MariaDB
    """
    try:
        conn = mariadb.connect(
            user="root",
            password="root",
            host="localhost",
            port=3306,
            database="data_collecteur"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return
    #
    # Cursor create
    #
    cur = conn.cursor()
    #
    # Execute SQL statement
    #
    cur.execute(sqlstatement)
    #
    # Commit DB
    #
    conn.commit()
    #
    # Close connection
    #
    conn.close()
    print(sqlstatement)


def main():
    """The main function"""
    while True:
        try:
            time.sleep(10)
            #
            # net counter
            # writing in file text
            #
            counter = get_net_io_counters()
            file_counter = f"Network counter: {counter}"
            write_to_file(file_counter)
            #
            # Write  network stats to DB
            #
            sql_statement = f"INSERT INTO network " \
                            f"(bytes_sent, bytes_received, packets_sent, packets_received) " \
                            f"VALUES " \
                            f"({bytes_sent}, {bytes_received}, {packets_sent}, {packets_received})"
            write_to_db(sql_statement)

            #
            # disk usage
            # writing in file text
            #
            disk = get_disk_usage()
            file_disk = f"Disk usage: {disk}"
            write_to_file(file_disk)
            #
            # Write  disk usage to DB
            #
            sql_statement = f"INSERT INTO disk " \
                            f"(total, used, free, percent) " \
                            f"VALUES " \
                            f"({total_disk}, {used_disk}, {free_disk}, {percent_disk})"
            write_to_db(sql_statement)

            #
            # memory stats
            # writing in file text
            #
            memory = get_memory_usage()
            file_memory = f"Memory stats: {memory}"
            write_to_file(file_memory)
            #
            # Write  memory stats to DB
            #
            sql_statement = f"INSERT INTO memory " \
                            f"(total, available, percent, used, free) " \
                            f"VALUES " \
                            f"({total_memory}, {available_memory}, {percent_memory}, {used_memory}, {free_memory})"
            write_to_db(sql_statement)

            #
            # cpu stats
            # writing in file text
            #
            cpu_percent = get_cpu_percent()
            file_cpu = f"Cpu percent: {cpu_percent} %"
            write_to_file(file_cpu)
            #
            # Write  cpu_percent to DB
            #
            sql_statement = f"INSERT INTO cpu_percent " \
                            f"(counter) " \
                            f"VALUES " \
                            f"({cpu_percent})"
            write_to_db(sql_statement)

            #
            # battery stats
            # writing in file text
            #
            battery = get_battery_level()
            file_battery = f"Battery level: {battery} %"
            write_to_file(file_battery)
            #
            # Write battery level to DB
            #
            sql_statement = f"INSERT INTO battery " \
                            f"(level) " \
                            f"VALUES " \
                            f"({battery})"

            write_to_db(sql_statement)

        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
