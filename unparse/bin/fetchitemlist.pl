#!/usr/bin/perl -I./bin/

use warnings;
use strict;

my $search_for=shift;
my $results_per_page=50;

my $base="http://unbisnet.un.org:8080";
# $base . "/ipac20/ipac.jsp?menu=search&aspect=alpha&npp=500&ipp=20&spp=20&profile=voting&ri=1&source=%7E%21horizon&index=Z791AZ&session&x=0&y=0&aspect=alpha&term=";
my $start= $base . '/ipac20/ipac.jsp?&menu=search&aspect=power&npp='. $results_per_page . '&ipp=20&spp=20&profile=bibga&index=.UD&sort=3100054&x=6&y=6&term=';
our $dbh;
use UNParse::Config;
# XXX we get some possibly useful XML out if we give GetXML=true in the query.

my $auth_page='http://daccessdds.un.org/prod/ods_mother.nsf?Login&Username=freeods2&Password=1234';
use LWP::UserAgent;
my $browser= LWP::UserAgent->new;
my %Uniques;

$browser->agent("s\@msmith.net");


# warn "$start\n";
{
	&setup_cookies();

	#&fetch_indices($start , 'SRES*');
	$search_for=~ s#[/ ]##g;
	&fetch_indices($start , $search_for .'*' );

	foreach my $k (sort keys %Uniques) {
		if ($ENV{DEBUG}) {warn "$k\n";}
		# print "$k\n";
		&fetch_doc($k);
	}
}

sub setup_cookies {
        my $url= shift;
        $browser->cookie_jar({});
        my $response = $browser->get($auth_page);
        # we don't need to do anything else
}


sub fetch_indices {
	my $url=shift;
	my $section= shift;
	my $page=1;
	my $carry_on=1;

	do {
		my $response= $browser->get($url. $section . '&page=' . $carry_on);

		if ($response->code == 200) {
			my $content= $response->{_content};
			$carry_on= &handle_page($content, $section);
		} else {
			die ("died fetching $url : " . $response->code . "\nmessage:\n" . $response->content);
		}


	} while ($carry_on);
}


sub handle_page {
	my $html= shift;
	my $section= shift;
	my ($interesting_fragment)= $html=~ m#Search Results(.*)Add/Remove MyList#msi;
	die "didn't match interesting_fragment in handle_page\n" . $html unless defined $interesting_fragment;
# warn $interesting_fragment;
# die;

	my @matches;

	(@matches)= $interesting_fragment=~ m#href="http://daccess-ods.un.org/access.nsf/Get\?Open&DS=([^>]+)&Lang=E"><font size="2">English#msgci;

	if (defined $ENV{DEBUG}) { warn join "\n found match ", @matches; }

	unless ($#matches) {
		warn "handle_page found no interesting_fragments\n";
	}
# </a></td><td><a class="smallBoldAnchor" title="View more information" href="http://unbisnet.un.org:8080/ipac20/ipac.jsp?session=H15L12140S258.2509&amp;profile=voting&amp;uri=link=3100027~!162580~!3100028~!3100069&amp;aspect=alpha&amp;menu=search&amp;ri=1&amp;source=~!horizon&amp;term=A%2F59%2FPV.1&amp;index=Z791AZ">A/59/PV.1</a></td><td><a class="smallBoldAnchor">20040914</a></td></tr><tr height="15" bgcolor="#FCFCDC"><td valign="top" width="2%">&nbsp;<a class="boldBlackFont1">
	foreach (@matches) {
		if (defined $ENV{DEBUG} ) { warn "found reference $_\n"; }
		$Uniques{$_}=undef;
	}

	if ($html=~ m#page%3D(\d+)[^<]*">Next</a>#i) 
	{
		warn "next page is turned off for development."; return (0);
		
		
		return ($1);
	} else {
		return (0);
	}
}


sub fetch_doc {
	my $code=shift;

	#my $query= $dbh->prepare("select * from documents where code=?");
	#$query->execute($code);
	#if ($query->fetchrow_hashref) { # and -d 'undocs/$code') {
	#	if ($ENV{DEBUG}) {warn "skipping undata/$code\n"}
	#	return;
	#} else {
	#	#system("mkdir", "-p", "undocs/$code"); # this is a security risk. But we'll trust the UN
	#}

	$browser->default_header('Referer' => $start);
	my $first_url='http://daccess-ods.un.org/access.nsf/Get?Open&DS=' . $code . '&Lang=E';
	my $response= $browser->get($first_url);

	if (defined $ENV{DEBUG}) {warn "fetching $code : $first_url\n"}

	# warn $response->content;
	#<META HTTP-EQUIV="refresh" CONTENT="0; URL=/TMP/640048.6.html">
	if ($response->content=~ m#0; URL=(.*?)">#) {
		$browser->default_header('Referer' => $first_url);
		if (defined $ENV{DEBUG}) {warn "    hoop2 is http://daccess-ods.un.org/$1\n"}
		$response= $browser->get("http://daccess-ods.un.org/" . $1);

		# <META HTTP-EQUIV="refresh" CONTENT="1; URL=http://daccessdds.un.org/doc/UNDOC/LTD/G94/641/66/PDF/G9464166.pdf?OpenElement">
		$response->content=~ m#CONTENT="1; URL=([^"]+)"#;
		my $url=$1;
		$dbh->do("insert into documents set code=?, url=?", undef, $code, $url);
		print "$code\t$url\n";
		$response= $browser->get($url);

print "$code\t$url\n"; return;

		if (defined $ENV{DEBUG}) {warn "    getting pdf $url\n"}

		$code=~s#/#\.#g;# to cope with julian's layout
		open (OUT, ">undocs/$code/original.pdf") || die "can't open undocs/$code/original.pdf:$!";
		print  OUT $response->content;
		close(OUT);
		$url=~s/PDF/DOC/;
		$url=~s/pdf/doc/;
		$response= $browser->get($url);
		if (defined $ENV{DEBUG}) {warn "    getting pdf $url\n"}

		open (OUT, ">undocs/$code/original.doc") or die "can't  open undocs/$code/original/doc:$!".
		print  OUT $response->content;
		close(OUT);
		# then fetch word doc
		#die;
	} else {
		warn "fetch_doc can't find URL in " . $response->content;
	}


}
