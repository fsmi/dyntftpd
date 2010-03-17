import boot_label

labels.append(LocalBootLabel(name = 'hdd', desc = 'Von ^Festplatte starten',
        help = 'Beendet den Netzwerkbootprozess und startet ' \
                'normal von der Festplatte.',
        default = True))

labels.append(ChainBootLabel(name = 'winxp', hd = 'hd0', part = 3,
        desc = '^Windows XP Professional',
        help = 'Startet Windows XP von der Festplatte.'))
labels.append(LinuxNfsRootBootLabel(name = 'linux', kernel = 'vmlinuz-i686',
        initrd = 'initrd.img-i686',
        nfsroot = 'nfsroot=10.14.1.3:/srv/nfs/clients/test,' \
                'v3,tcp,rsize=32768,wsize=32768',
        append = 'quiet vga=normal ramdisk_size=14332 ' \
                'ro init=/usr/local/sbin/startup DISK=/dev/hda1',
        desc = '^FSMI Linux (Kernel: aktuell / Image: test)'))

labels.append(SeparatorBootLabel(desc = 'Admin:'))
labels.append(LinuxBootLabel(name = 'rescue', kernel = 'd-i/linux-etch-i386',
        initrd = 'd-i/initrd-etch-i386',
        append = 'vga=normal rescue/enable=true --',
        desc = '^Wiederherstellungskonsole',
        help = 'Startet einen Debian-Installer (etch/i386) im ' \
                'Rescue Mode.',
        password = '<placeholder>', indent = 1))
labels.append(LinuxBootLabel(name = 'install', kernel = 'd-i/linux-etch-i386',
        initrd = 'd-i/initrd-etch-i386', append = 'vga=normal --',
        desc = '^Debian-Installer (etch/i386)',
        help = 'Startet einen Debian-Installer (etch/i386).',
        password = '<placeholder>', indent = 1))

# vim:set ft=python sw=4 et:
