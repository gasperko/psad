%define name psad
%define version 1.3.2
%define release 1
%define psadlibdir /usr/lib/psad
%define psadlogdir /var/log/psad
%define psadrundir /var/run/psad
%define psadvarlibdir /var/lib/psad
#%define psadetcdir /etc/psad

### get the first @INC directory that includes the string "linux".
### This may be 'i386-linux', or 'i686-linux-thread-multi', etc.
%define psadmoddir `perl -e '$path='i386-linux'; for (@INC) { if($_ =~ m|.*/(.*linux.*)|) {$path = $1; last; }} print $path'`

Summary: Psad analyzes iptables log messages for suspect traffic
Name: %name
Version: %version
Release: %release
License: GPL
Group: System/Servers
Url: http://www.cipherdyne.org/psad/
Source: %name-%version.tar.gz
BuildRoot: %_tmppath/%{name}-buildroot
Requires: smtpdaemon
Requires: iptables
#Prereq: rpm-helper

%description
Port Scan Attack Detector (psad) is a collection of three lightweight
system daemons written in Perl and in C that are designed to work with Linux
iptables firewalling code to detect port scans and other suspect traffic.  It
features a set of highly configurable danger thresholds (with sensible
defaults provided), verbose alert messages that include the source,
destination, scanned port range, begin and end times, tcp flags and
corresponding nmap options, reverse DNS info, email and syslog alerting,
automatic blocking of offending ip addresses via dynamic configuration of
iptables rulesets, and passive operating system fingerprinting.  In addition,
psad incorporates many of the tcp, udp, and icmp signatures included in the
snort intrusion detection system (http://www.snort.org) to detect highly
suspect scans for various backdoor programs (e.g. EvilFTP, GirlFriend,
SubSeven), DDoS tools (mstream, shaft), and advanced port scans (syn, fin,
xmas) which are easily leveraged against a machine via nmap.  psad can also
alert on snort signatures that are logged via fwsnort
(http://www.cipherdyne.org/fwsnort/), which makes use of the
iptables string match module to detect application layer signatures.


%prep
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%setup -q

cd Psad && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ..
cd IPTables/Parse && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ../..
cd Bit-Vector && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ..
cd Net-IPv4Addr && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ..
cd Unix-Syslog && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ..
cd Date-Calc && perl Makefile.PL PREFIX=%psadlibdir LIB=%psadlibdir
cd ..

%build
### build psad binaries (kmsgsd and psadwatchd)
make OPTS="$RPM_OPT_FLAGS"

### build the whois client
make OPTS="$RPM_OPT_FLAGS" -C whois

### build perl modules used by psad
make OPTS="$RPM_OPT_FLAGS" -C Psad
make OPTS="$RPM_OPT_FLAGS" -C IPTables/Parse
make OPTS="$RPM_OPT_FLAGS" -C Bit-Vector
make OPTS="$RPM_OPT_FLAGS" -C Net-IPv4Addr
make OPTS="$RPM_OPT_FLAGS" -C Unix-Syslog
make OPTS="$RPM_OPT_FLAGS" -C Date-Calc

%install
### config directory
#mkdir -p $RPM_BUILD_ROOT%psadetcdir
### log directory
mkdir -p $RPM_BUILD_ROOT%psadlogdir
### dir for psadfifo
mkdir -p $RPM_BUILD_ROOT%psadvarlibdir
### dir for pidfiles
mkdir -p $RPM_BUILD_ROOT%psadrundir

### psad module dirs
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Bit/Vector
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Bit
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Psad
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Unix/Syslog
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Date/Calc
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Net/IPv4Addr
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/IPTables/Parse
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Unix
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Carp
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calc
mkdir -p $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar
mkdir -p $RPM_BUILD_ROOT%psadlibdir/auto/Net/IPv4Addr
mkdir -p $RPM_BUILD_ROOT%psadlibdir/Net
mkdir -p $RPM_BUILD_ROOT%psadlibdir/IPTables

### whois_psad binary
mkdir -p $RPM_BUILD_ROOT%_bindir
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8
mkdir -p $RPM_BUILD_ROOT%_sbindir
### psad config
mkdir -p $RPM_BUILD_ROOT%_sysconfdir/%name
### psad init script
mkdir -p $RPM_BUILD_ROOT/etc/rc.d/init.d

install -m 500 {psad,kmsgsd,psadwatchd} $RPM_BUILD_ROOT%_sbindir/
install -m 500 fwcheck_psad.pl $RPM_BUILD_ROOT%_sbindir/fwcheck_psad
install -m 755 whois/whois $RPM_BUILD_ROOT/usr/bin/whois_psad
install -m 755 psad-init.redhat $RPM_BUILD_ROOT/etc/rc.d/init.d/psad
install -m 644 {psad.conf,kmsgsd.conf,psadwatchd.conf,fw_search.conf} $RPM_BUILD_ROOT%_sysconfdir/%name/
install -m 644 {signatures,icmp_types,auto_dl,posf} $RPM_BUILD_ROOT%_sysconfdir/%name/
install -m 644 *.8 $RPM_BUILD_ROOT%{_mandir}/man8/

### install perl modules used by psad
install -m 555 Bit-Vector/blib/arch/auto/Bit/Vector/Vector.so $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Bit/Vector/Vector.so
install -m 444 Bit-Vector/blib/arch/auto/Bit/Vector/Vector.bs $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Bit/Vector/Vector.bs
install -m 444 Bit-Vector/blib/lib/Bit/Vector.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Bit/Vector.pm
install -m 555 Unix-Syslog/blib/arch/auto/Unix/Syslog/Syslog.so $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Unix/Syslog/Syslog.so
install -m 444 Unix-Syslog/blib/arch/auto/Unix/Syslog/Syslog.bs $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Unix/Syslog/Syslog.bs
install -m 444 Unix-Syslog/blib/lib/auto/Unix/Syslog/autosplit.ix $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Unix/Syslog/autosplit.ix
install -m 444 Unix-Syslog/blib/lib/Unix/Syslog.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Unix/Syslog.pm
install -m 555 Date-Calc/blib/arch/auto/Date/Calc/Calc.so $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Date/Calc/Calc.so
install -m 444 Date-Calc/blib/arch/auto/Date/Calc/Calc.bs $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/auto/Date/Calc/Calc.bs
install -m 444 Date-Calc/blib/lib/Carp/Clan.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Carp/Clan.pod
install -m 444 Date-Calc/blib/lib/Carp/Clan.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Carp/Clan.pm
install -m 444 Date-Calc/blib/lib/Date/Calc.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calc.pm
install -m 444 Date-Calc/blib/lib/Date/Calc.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calc.pod
install -m 444 Date-Calc/blib/lib/Date/Calendar.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar.pm
install -m 444 Date-Calc/blib/lib/Date/Calendar.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar.pod
install -m 444 Date-Calc/blib/lib/Date/Calc/Object.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calc/Object.pm
install -m 444 Date-Calc/blib/lib/Date/Calc/Object.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calc/Object.pod
install -m 444 Date-Calc/blib/lib/Date/Calendar/Year.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar/Year.pm
install -m 444 Date-Calc/blib/lib/Date/Calendar/Profiles.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar/Profiles.pod
install -m 444 Date-Calc/blib/lib/Date/Calendar/Profiles.pm $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar/Profiles.pm
install -m 444 Date-Calc/blib/lib/Date/Calendar/Year.pod $RPM_BUILD_ROOT%psadlibdir/%psadmoddir/Date/Calendar/Year.pod
install -m 444 Net-IPv4Addr/blib/lib/auto/Net/IPv4Addr/autosplit.ix $RPM_BUILD_ROOT%psadlibdir/auto/Net/IPv4Addr/autosplit.ix
install -m 444 Net-IPv4Addr/blib/lib/Net/IPv4Addr.pm $RPM_BUILD_ROOT%psadlibdir/Net/IPv4Addr.pm
install -m 444 IPTables/Parse/Parse.pm $RPM_BUILD_ROOT%psadlibdir/IPTables/Parse.pm
install -m 444 Psad/Psad.pm $RPM_BUILD_ROOT%psadlibdir/Psad.pm

### install snort rules files
cp -r snort_rules $RPM_BUILD_ROOT%_sysconfdir/%name

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%pre
#if [ ! -p /var/lib/psad/psadfifo ];
#then [ -e /var/lib/psad/psadfifo ] && /bin/rm -f /var/lib/psad/psadfifo
#fi
#/bin/mknod -m 600 /var/lib/psad/psadfifo p
#chown root.root /var/lib/psad/psadfifo
#chmod 0600 /var/lib/psad/psadfifo

%post
### put the current hostname into the psad C binaries
### (kmsgsd and psadwatchd).
perl -p -i -e 'use Sys::Hostname; my $hostname = hostname(); s/HOSTNAME(\s+)_?CHANGE.?ME_?/HOSTNAME${1}$hostname/' %_sysconfdir/%name/psad.conf
perl -p -i -e 'use Sys::Hostname; my $hostname = hostname(); s/HOSTNAME(\s+)_?CHANGE.?ME_?/HOSTNAME${1}$hostname/' %_sysconfdir/%name/psadwatchd.conf

/bin/touch %psadlogdir/fwdata
chown root.root %psadlogdir/fwdata
chmod 0600 %psadlogdir/fwdata
if [ ! -p %psadvarlibdir/psadfifo ];
then [ -e %psadvarlibdir/psadfifo ] && /bin/rm -f %psadvarlibdir/psadfifo
/bin/mknod -m 600 %psadvarlibdir/psadfifo p
fi
chown root.root %psadvarlibdir/psadfifo
chmod 0600 %psadvarlibdir/psadfifo
### make psad start at boot
/sbin/chkconfig --add psad
[ -f /etc/syslog.conf ] || exit 0
### make a backup of /etc/syslog.conf
[ -f /etc/syslog.conf.orig ] || cp -p /etc/syslog.conf /etc/syslog.conf.orig
### add the psadfifo line to /etc/syslog.conf if necessary
if ! grep -v "#" /etc/syslog.conf | grep -q psadfifo;
then echo " .. Adding psadfifo line to /etc/syslog.conf"
echo "kern.info |/var/lib/psad/psadfifo" >> /etc/syslog.conf
fi
if [ -e /var/run/syslogd.pid ];
then
echo " .. Restarting syslogd "
kill -HUP `cat /var/run/syslogd.pid`
fi
if grep -q "EMAIL.*root.*localhost" /etc/psad/psad.conf;
then
echo " .. You can edit the EMAIL_ADDRESSES variable in /etc/psad/psad.conf"
echo "    /etc/psad/psadwatchd.conf to have email alerts sent to an address"
echo "    other than root\@localhost"
fi

if grep -q "HOME_NET.*CHANGEME" /etc/psad/psad.conf;
then
echo " .. Be sure to edit the HOME_NET variable in /etc/psad/psad.conf"
echo "    to define the internal network(s) attached to your machine."
fi

%preun
#%_preun_service psad

%files
%defattr(-,root,root)
%dir %psadlogdir
%dir %psadvarlibdir
%dir %psadrundir
/etc/rc.d/init.d/psad
%_sbindir/*
%_bindir/*
%{_mandir}/man8/*

%dir %_sysconfdir/%name
%config(noreplace) %_sysconfdir/%name/*.conf
%config(noreplace) %_sysconfdir/%name/signatures
%config(noreplace) %_sysconfdir/%name/auto_dl
%config(noreplace) %_sysconfdir/%name/posf
%config(noreplace) %_sysconfdir/%name/icmp_types

%dir %_sysconfdir/%name/snort_rules
%config(noreplace) %_sysconfdir/%name/snort_rules/*

%_libdir/%name

%changelog
* Mon Oct 14 2003 Michael Rash <mbr@cipherydne.org>
- Removed ipchains text from description.
- Added test and config warning message for HOME_NET variable.
- Updated to version 1.3

* Mon Oct 14 2003 Michael Rash <mbr@cipherydne.org>
- Removed diskmond since psad handles disk space thresholds
  directly.

* Sat Oct 11 2003 Michael Rash <mbr@cipherydne.org>
- Updated spec file to build properly on both Red Hat 7.2 and
  Red Hat 9 systems.

* Tue Sep 23 2003 Lenny Cartier <lenny@mandrakesoft.com> 1.2.3-1mdk
- mandrakized specfile

* Fri Sep 12 2003 Michael Rash <mbr@cipherdyne.org>
- Added interface tracking for scans.
- Bugfix for not opening /etc/hosts.deny the right way in
  tcpwr_block().
- Bugfix for psadfifo path in syslog-ng config.
- Better format for summary stats section in email alerts.
- Bugfix for INIT_DIR path on non-RedHat systems.
- Bugfix for gzip path.
- Make Psad.pm installed last of all perl modules installed
  by psad.
- Added additional call to incr_syscall_ctr() in psadwatchd.c

* Mon Jul 28 2003 Michael Rash <mbr@cipherdyne.org>
- Initial version.
