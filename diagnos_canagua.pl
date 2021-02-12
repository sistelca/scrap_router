#!/usr/bin/perl -w
# programa para leer archivo de control de clientes


# leer archivo canagua.txt
open(FH, '<', 'canagua.txt') or die $!;

while(<FH>){
    $estado = $_;
}

close(FH);


$diagno1 = system "/usr/bin/ping 192.168.45.38 -c 2 ";
$diagno2 = system "/usr/bin/ping 192.168.45.71 -c 2 ";
$diagno3 = system "/usr/bin/ping 192.168.40.78 -c 2 ";


open(my $fh, '>', 'canagua.txt');

if($diagno1==256 && $diagno2==256 && $diagno3==256 && $estado==0) {
    system "/root/taller/ledc 1";
    sleep(20);
    system "/root/taller/ledc 0";
    sleep(20);

    $d = system "/usr/bin/ping 192.168.45.38 -c 2 ";
    $i = system "/usr/bin/ping 192.168.45.71 -c 2 ";
    $a = system "/usr/bin/ping 192.168.40.78 -c 2 ";

    if($d==256 && $i==256 && $a==256) {
        $estado = "1";
    }
} elsif($diagno1==0 || $diagno2==0 || $diagno3==0) {
    $estado = "0";
}

print $fh $estado;
close $fh;
