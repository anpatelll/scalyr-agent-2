#!/usr/bin/env python
import re

__author__ = 'czerwin'

import sys

from optparse import OptionParser

from scalyr_agent.__scalyr__ import scalyr_init

scalyr_init()

from scalyr_agent.monitors_manager import load_monitor_class

__monitors__ = []

__monitors__.append(['mysql',
"""|||# ``module``               ||| Always ``scalyr_agent.builtin_monitors.shell_monitor``
|||# ``id``                   ||| Included in each log message generated by this monitor, as a field named ``instance``. \\
                                  Allows you to distinguish between values recorded by different monitors.
|||# ``command``              ||| The shell command to execute.
|||# ``extract``              ||| Optional: a regular expression to apply to the command output. If defined, this \\
                                  expression must contain a matching group (i.e. a subexpression enclosed in parentheses). \\
                                  The monitor will record only the content of that matching group. This allows you to discard \\
                                  unnecessary portions of the command output and extract the information you need.
|||# ``log_all_lines``        ||| Optional (defaults to false). If true, the monitor will record the entire command output; \\
                                  otherwise, it only records the first line.
|||# ``max_characters``       ||| Optional (defaults to 200). At most this many characters of output are recorded. \\
                                  You may specify a value up to 10000, but the Scalyr server currently truncates all \\
                                  fields to 3500 characters.""",
"""#   proc.stat.cpu type=*:        CPU counters in units of jiffies, where type can be one of user, nice, system, iowait,
#                                irq, softirq, steal, guest.  As a rate, they should add up to 100*numcpus on the host.
#   proc.stat.intr:              The number of interrupts since boot.
#   proc.stat.ctxt               The number of context switches since boot.
#   proc.stat.processes          The number of processes created since boot.
#   proc.stat.procs_blocked      The number of processes currently blocked on I/O.
#   proc.loadavg.1m              The load average over 1 minute.
#   proc.loadavg.5m              The load average over 5 minutes.
#   proc.loadavg.15m             The load average over 15 minutes.
#   proc.loadavg.runnable        The number of runnable threads/processes.
#   proc.loadavg.total_threads   The total number of threads/processes.
#   proc.kernel.entropy_avail    The number of bits of entropy that can be read without blocking from /dev/random
#   proc.uptime.total            The seconds since boot.
#   proc.uptime.now              The seconds since boot of idle time
#   proc.vmstat.pgfault          The number of minor page faults since boot.
#   proc.vmstat.pgmajfault       The number of major page faults since boot
#   proc.vmstat.pswpin           The number of processes swapped in since boot.
#   proc.vmstat.pswpout          The number of processes swapped out since boot.
#   proc.vmstat.pgppin           The number of pages swapped in since boot.
#   proc.vmstat.pgpout           The number of pages swapped out in since boot.
#   sys.numa.zoneallocs, type=*, node=*
#                                The number of pages allocated from the preferred node, either type=hit or type=miss.
#   sys.numa.foreign_allocs, node=*
#                                The number of pages allocated from node because the preferred node did not have any free.
#   sys.numa.allocation, node=*, type=*
#                                The number of pages allocated either type=locally or type=remotely for processes on this
#                                node.
#   sys.numa.interleave, node=*, type=hit
#                                The number of pages allocated successfully by the interleave strategy.
#   net.sockstat.num_sockets     The number of sockets allocated (only TCP).
#   net.sockstat.num_timewait    The number of TCP sockets currently in TIME_WAIT state.
#   net.sockstat.sockets_inuse, type=*
#                                The number of sockets in use by type.
#   net.sockstat.num_orphans     The number of orphan TCP sockets (not attached to any file descriptor).
#   net.sockstat.memory, type=*  Memory allocated for this socket type (in bytes).
#   net.sockstat.ipfragqueues    The number of IP flows for which there are currently fragments queued for reassembly.
#   net.stat.tcp.abort, type=*   The number of connections that the kernel had to abort due broken down by reason.
#   net.stat.tcp.abort.failed    The number of times the kernel failed to abort a connection because it didn't even have
#                                enough memory to reset it.
#   net.stat.tcp.congestion.recovery, type=*
#                                The number of times the kernel detected spurious retransmits and was able to recover part
#                                or all of the CWND, broken down by how it recovered.
#   net.stat.tcp.delayedack, type=*
#                                The number of delayed ACKs sent of different types.
#   net.stat.tcp.failed_accept, reason=*
#                                The number of times a connection had to be dropped  after the 3WHS.  reason=full_acceptq
#                                indicates that the application isn't accepting connections fast enough.  You should
#                                see SYN cookies too.
#   net.stat.tcp.invalid_sack, type=*
#                                The number of invalid SACKs we saw of diff types. (requires Linux v2.6.24-rc1 or newer)
#   net.stat.tcp.memory.pressure The number of times a socket entered the "memory pressure" mode.
#   net.stat.tcp.memory.prune, type=*
#                                The number of times a socket had to discard received data due to low memory conditions,
#                                broken down by type.
#   net.stat.tcp.packetloss.recovery, type=*
#                                The number of times we recovered from packet loss by type of recovery (e.g. fast
#                                retransmit vs SACK).
#   net.stat.tcp.receive.queue.full
#                                The number of times a received packet had to be dropped because the socket's receive
#                                queue was full (requires Linux v2.6.34-rc2 or newer)
#   net.stat.tcp.reording, detectedby=*
#                                The number of times we detected re-ordering broken down by how.
#   net.stat.tcp.syncookies, type=*
#                                SYN cookies (both sent & received).
#   iostat.disk.read_requests, dev=*
#                                The number of reads completed by device
#   iostat.disk.read_merged, dev=*
#                                The number of reads merged by device
#   iostat.disk.read_sectors, dev=*
#                                The number of sectors read by device
#   iostat.disk.msec_read, dev=*   Time in msec spent reading by device
#   iostat.disk.write_requests, dev=*
#                                The number of writes completed by device
#   iostat.disk.write_merged, dev=*
#                                The number of writes merged by device
#   iostat.disk.write_sectors, dev=*
#                                The number of sectors written by device
#   iostat.disk.msec_write, dev=* Time in msec spent writing by device
#   iostat.disk.ios_in_progress, dev=*
#                                The number of I/O operations in progress by device
#   iostat.disk.msec_total, dev=*  Time in msec doing I/O by device
#   iostat.disk.msec_weighted_total, dev=*
#                                Weighted time spent performing I/O (multiplied by ios_in_progress) by device
#   df.1kblocks.total, mount=*, fstype=*
#                              The total size of the file system broken down by mount and filesystem type.
#   df.1kblocks.used, mount=*, fstype=*
#                              The number of blocks used broken down by mount and filesystem type.
#   df.1kblocks.available, mount=*, fstype=*
#                              The number of locks available broken down by mount and filesystem type.
#   df.inodes.total, mount=*, fstype=*
#                              The total number of inodes broken down by mount and filesystem type.
#   df.inodes.used, mount=*, fstype=*
#                              The number of used inodes broken down by mount and filesystem type.
#   df.inodes.free, mount=*, fstype=*
#                              The number of free inodes broken down by mount and filesystem type.
#   proc.net.bytes, iface=*, direction=*
#                              The number of bytes through the interface broken down by interface and direction.
#   proc.net.packets, iface=*, direction=*
#                              The number of packets through the interface broken down by interface and direction.
#   proc.net.errs, iface=*, direction=*
#                              The number of packet errors broken down by interface and direction.
#   proc.net.dropped, iface=*, direction=*
#                              The number of dropped packets broken down by interface and direction."""])


def do_back_convert(module_name, config_section, metric_section):
    print 'Output for %s' % module_name

    metric_lines = parse_metric_lines(metric_section)
    for metric in metric_lines:
        extra_one = None
        extra_two = None
        tokens = metric.split(' ')
        metric_name = tokens.pop(0)

        if metric_name.endswith(','):
            metric_name = metric_name.strip(',')
            extra_one = tokens.pop(0)

            if extra_one.endswith(','):
                extra_one = extra_one.strip(',')
                extra_two = tokens.pop(0)

        extra_fields = {}
        if extra_one is not None:
            extract_extra(extra_one, extra_fields)
        if extra_two is not None:
            extract_extra(extra_two, extra_fields)

        metric_description = ' '.join(tokens)

        print 'define_metric(__monitor__, \'%s\',' % metric_name
        sys.stdout.write('              \'')
        indent_length = len('define_metric(')
        write_wrapped_line(metric_description, 120 - indent_length, '%s\'' % space_filler(indent_length))
        sys.stdout.write('\'')
        if len(extra_fields) > 0:
            sys.stdout.write(',\n%sextra_fields={' % space_filler(indent_length))
            massaged_fields = []
            for key in extra_fields.iterkeys():
                value = extra_fields[key]
                massaged_fields.append('\'%s\': \'%s\'' % (key, value))
            sys.stdout.write(', '.join(massaged_fields))
            sys.stdout.write('}')
        print ')'

def extract_extra(field, thedict):
    if field.endswith('=*'):
        thedict[field[0:-2]] = ''
    elif field.find('=') >= 0:
        x = field.find('=')
        thedict[field[0:x]] = field[x+1:]
    else:
        thedict[field] = ''

def parse_metric_lines(metric_section):
    result = []
    for line in metric_section.split('\n'):
        without_pound = line[1:]
        if len(without_pound) > 3 and without_pound[3] == ' ':
            result[-1] = '%s %s' % (result[-1], without_pound.strip())
        else:
            result.append(without_pound.strip())
    return result

def write_wrapped_line(content, wrap_length, line_prefix):
    """Writes content to stdout but breaking it after ``wrap_length`` along space boundaries.

    When it begins a new line, ``line_prefix`` is printed first.

    @param content: The line to write
    @param wrap_length: The maximum size of any line emitted.  After this length, the line will be wrapped.
    @param line_prefix: The prefix to write whenenver starting a new line

    @type content: str
    @type wrap_length: int
    @type line_prefix: str
    """
    current_line = ''
    for word in content.split(' '):
        if len(current_line) + len(word) + 3 > wrap_length:
            sys.stdout.write(current_line)
            sys.stdout.write(' \'\n')
            sys.stdout.write(line_prefix)
            current_line = word
        elif len(current_line) == 0:
            current_line = word
        else:
            current_line = '%s %s' % (current_line, word)

    if len(current_line) > 0:
        sys.stdout.write(current_line)


def space_filler(num_spaces):
    """Returns a string with the specified number of spaces.

    @param num_spaces: The number of spaces
    @type num_spaces: int
    @return: The string
    @rtype: str
    """
    return ' ' * num_spaces


def extra_text(input_str):
    return re.split('``', input_str)[1]

def break_by_lines(input):
    """

    @param input:
    @type input: str
    @return:
    @rtype:
    """
    result = []

    add_previous = False
    for line in input.split('\n'):
        ends_in_cont = line.endswith('\\')
        if ends_in_cont:
            line = line[0:-2].rstrip()
        if add_previous:
            result[-1] = '%s %s' % (result[-1], line.strip())
        else:
            result.append(line)
        add_previous = ends_in_cont

    return result


if __name__ == '__main__':
    for entry in __monitors__:
        do_back_convert(entry[0], entry[1], entry[2])