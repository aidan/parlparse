#!/usr/bin/perl

package UNParse::Routines;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(parse_file &show_txt);  # symbols to export on request
use warnings;
use strict;
our $dbh= $main::dbh || die "main dbh contains nothing\n";

sub parse_file {
	my $filename= shift;
	my $docid= shift;

	if (not -e $filename) {
		warn "file does not exist: $filename";
	} else {
		if ($filename=~ m#\w+/A/#) {
			&submit_to_db($docid, &parse_file_A($filename));
		} elsif ($filename=~ m#\w+/S/RES#) {# Resolutions
			&submit_to_db($docid, &parse_file_S_RES($filename));
		} elsif ($filename=~ m#\w+/S/PRST#) {# press release statement
			&submit_to_db($docid, &parse_file_S_PRST($filename));
		} elsif ($filename=~ m#\w+/S/PV#) {# press release statement
			&submit_to_db($docid, &parse_file_S_PV($filename));
		} else {
			warn "unknown category for parsing: $filename\n";
		}
	}

	# now need to look through db to find the date and title
	# of document and hence populate documents tabl and also populate the
	# first_seen column so alerts work 

}

our %fonts;

sub parse_file_A {
	return (&parse_file_no_names(@_));
}

sub parse_file_S_RES {
	return (&parse_file_no_names(@_));
}

sub parse_file_S_PRST {
	return (&parse_file_no_names(@_));
}

sub parse_file_S_PV {
	return (&look_for_names_S_PV(&parse_file_no_names(@_)));
}



sub look_for_names_S_PV {
	my @paras=@_;
	# quickly, look for the words "issued in place of a verbatim record"

	foreach my $p (@paras) {
		if ($p->{content} =~ m#the following communiqu. was issued through the Secretary-General in place of a verbatim record#i)  {
			return (@paras); # closed session, so don't bother putting speakers in.
		} elsif ($p->{content} =~ m#President of the Security Council made the following statement on behalf of the Council#i)  {
                        return (@paras); # statement rather than transcript
                }
	}

	# <b>Mr. Adada</b> (Congo) (<i>spoke in French</i>): 

	return (@paras);

}


sub parse_file_no_names {
	# we deliberately don't do this using an xml parser.
	my $filename= shift;

	open (FILE, $filename) || die "parse_file_A can't open $filename:$!";
	my @lines= <FILE>;
	close (FILE);

	my $line;
	my @content;
	do {$line= shift @lines}  while ($line and $line !~ /<pdf2xml>/); # preamble
	my %cache;
	foreach $line (@lines) {
		if ($line =~ m#<page.*?number="(\d+)"#) {
			$cache{'page'}=$1;
			# print "page = $1\n";
		} elsif ($line =~ m#<fontspec id="(\d+)" size="([-\d]+)" family="([^"]+)" color="([^"]*)"#i ) {
			$fonts{$1}->{size}=$2;
			$fonts{$1}->{family}=$3;
			$fonts{$1}->{color}=$4;
		} elsif ($line=~ m#<text top="(\d+)" left="(\d+)" width="(\d+)" height="(\d+)" font="(\d+)">(.*)</text>#i) {
			my $line;
			$line->{'top'}=$1;
			$line->{'left'}=$2;
			$line->{'width'}=$3;
			$line->{'height'}=$4;
			$line->{'font'}=$5;
			$line->{'font_size'}=$fonts{$5}->{size};
			$line->{'font_family'}=$fonts{$5}->{family};
			$line->{'content'}=$6;
			$line->{'page'}= $cache{'page'};
			push @content, $line;
		} elsif ($line =~ m#</page>#) { # do nothing
		} elsif ($line =~ m#</pdf2xml>#) { # do nothing
		} else {
			warn "parse_file_A unmatched line $line\n";
		}
	}


	return(&to_paragraphs_A(@content));
}

sub to_paragraphs_A {
	# take a list of raw lines, and then munger thme to put paragraphs
	# back together out of sequences of identically formatted sequential lines
	my @lines= ({},@_); # we need empty element as stuff can stutter forwards one
	my @paragraphs;
	my %last;
	my $highlight;

	$last{'highlight'}='';
	$last{'font'}=rand;

	foreach my $index (1 .. $#lines) {
		$highlight='';
		if ((defined $lines[$index] and defined $lines[$index]->{content}) and $lines[$index]->{content} =~ m#<([bi])>.*</\1>#){
			$highlight=$1;
			$lines[$index]->{content}=~ s#</?$highlight>##g;
		}

		# print "==$lines[$index]->{font_size} $highlight== - $lines[$index]->{content}\n";

		if ($last{'highlight'} eq $highlight  and $last{'font'} == $lines[$index]->{font}) {
			# this line has same formatting as the previous one.
			if ($lines[$index]->{content} =~ m#^(?:<(.)>)?\s*(?:</\1>)?$#) {
				# empty line denoting paragraph break. flag prev line
				$lines[$index-1]->{end_para}= 1;
				$lines[$index]->{start_para}= 1;
			}
		} else { # this is a different paragraph. flag prev and this
			$lines[$index-1]->{end_para}= 1;
			$lines[$index]->{start_para}= 1;
		}
		$last{'font'}= $lines[$index]->{font};
		$last{'highlight'}= $highlight;
	}
	$lines[$#lines]->{end_para}=1; # can't just fall off the end

	my $counter;
	my $content;
	my %cache;

	# go through the lines to find the start/end of paras
	# cache location at start and store at the end;
	foreach my $index (1 .. $#lines ) {
		$content .= $lines[$index]->{content};
		my $para;

		if (defined $lines[$index]->{start_para}) { # line can be both start and end of para
			$cache{'top'}=$lines[$index]->{'top'};
			$cache{'left'}=$lines[$index]->{'left'};
			$cache{'width'}=$lines[$index]->{'width'};
			$cache{'height'}=$lines[$index]->{'height'};
			$cache{'font'}=$lines[$index]->{'font'};
			$cache{'font_size'}=$lines[$index]->{'font_size'};
			$cache{'font_family'}=$lines[$index]->{'font_family'};
			$cache{'page'}= $lines[$index]->{'page'};
		}

		if (defined $lines[$index]->{end_para}) {
			next if ($content =~ m#^\s*$#);
			print ++$counter . " is counter; $lines[$index]->{font} is font; ==$content==\n\n";
			$para->{'content'}= $content;
			$para->{'top'}=$cache{'top'};
			$para->{'left'}=$cache{'left'};
			$para->{'width'}=$cache{'width'};
			$para->{'height'}=$cache{'height'};
			$para->{'font'}=$cache{'font'};
			$para->{'font_size'}=$cache{'font_size'};
			$para->{'font_family'}=$cache{'font_family'};
			$para->{'page'}= $cache{'page'};
			$para->{'counter'}= $counter;


			push @paragraphs, $para;
			$content='';
		}
	}
	return (@paragraphs);
}




sub submit_to_db {
	my ($docid, @paras)= @_;
	my $previous=0;

	my %font_standard;
	my $order;
	foreach my $f (reverse (sort {$fonts{$a}->{size} <=> $fonts{$b}->{size}} keys %fonts)) {
		$font_standard{$fonts{$f}->{size}}= ++$order;
	}

	my $query= $dbh->prepare("insert into contents 
		     set documentid=?,
		         position=?,
		         pos_top=?,
			 pos_left=?,
			 pos_width=?,
			 pos_height=?,
			 fontid=?,
			 fontid_standard=?,
			 page=?,
			 previous_contentid=?,
			 speakerid=?
		") ;

	foreach my $p (@paras) {
		$p->{speakerid} ||=0;
		$query->execute(
				$docid,
				$p->{counter},
				$p->{top},
				$p->{left},
				$p->{width},
				$p->{height},
				$p->{font_size},
				$font_standard{$p->{font}},
				$p->{page},
				$previous,
				$p->{speakerid}
			) || die "died in submit_to_db for doc $docid: " .  $dbh->errstr;

		$previous=$dbh->{mysql_insertid};

		$dbh->do("insert into text set contentid=$previous, text=?", undef, $p->{content});
		$dbh->do("update documents set new=0 where ourdocid=$docid");
	}
}


sub show_txt {
	my $documentid= shift;

	my $query= $dbh->prepare("select * from contents,text where documentid=?
				  and contents.contentid=text.contentid")
		 || $dbh->errstr;
	$query->execute($documentid);

	my $result;

	while ($result= $query->fetchrow_hashref) {
		# print "==========\n";
		# print "$result->{position}:$result->{fontid}:$result->{text}\n\n";
	}
}

1;




