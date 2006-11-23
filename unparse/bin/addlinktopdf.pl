#!/usr/bin/perl

# Early code from Sams, not sure where used

use warnings;
use strict;
use PDF::Reuse;
my $pdf= shift || die &usage();

{
	prFile($pdf . ".linked.pdf");

	while (my $line =<STDIN>) {
		chomp($line);
		$line=~ s#^\s*##;
		prLink(split /[\s]+/, $line);
	}

	prDoc($pdf);
	prEnd();
}





sub usage {
	die "usage: $0 filename.pdf\nprovide lines on STDIN matching:\n\t\tpageno\tx\ty\twidth\theight\tURI\n";
}

