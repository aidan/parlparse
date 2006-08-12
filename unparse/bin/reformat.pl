#!/usr/bin/perl -I./bin/

use warnings;
use strict;

our $dbh;
use UNParse::Config;
use UNParse::Routines;

{
	my $query= $dbh->prepare("select * from documents where new=1");
	$query->execute || die "can't execute query : $!";

	while (my $row=$query->fetchrow_hashref) {
		&process_file($row);
	}
}

sub process_file {
	my $ref= shift;

	#chdir ("undocs/$ref->code") || die "can't chdir to undocs/$ref->{code}:$!";
print "$ref->{code}\n";

	my $xml_file= "undocs/$ref->{code}/out";
	system("pdftohtml", "-xml", "undocs/$ref->{code}/original.pdf", $xml_file);
	$xml_file.='.xml';

	print STDERR "$xml_file\n";
	&parse_file($xml_file, $ref->{ourdocid});
}
