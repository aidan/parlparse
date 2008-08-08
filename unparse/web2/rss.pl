#!/usr/bin/perl

use warnings;
use strict;
use XML::RSS;
use CGI qw/param/;
use DBI;
use File::Basename;
use Data::Dumper;

my $dbh;
my %Config;
my $search;


{
    &setup;

    my $q= $dbh->prepare("select * from rsscache where term=? and generated  >= date_sub(now(), interval 24 hour)");
    $q->execute($search);
    if (my $r= $q->fetchrow_hashref) {
        print "Content-Type: text/xml\n\n";
        print $r->{'content'};
    } else  {
        &output(&process);
    }
}


sub output {
    my $results= shift;

        # create an RSS 0.9 file
        use XML::RSS;
        my $rss = new XML::RSS (version => '0.91');
        $rss->channel(title => "UNDemocracy RSS feed",
                      link  => "http://undemocracy.com",
                      description => "UNDemocracy.com"
                      );


        foreach my $file (keys %$results) {
            my $web_link= $file;

            if ($web_link=~ m#S\-PV-(.*)#) {
                $web_link= "securitycouncil/meeting_" . $1;
            } elsif ($web_link =~ m#A-(\d+)-PV\.(.*)#) {
                $web_link= "generalassembly_$1/meeting_$2"
            }

            foreach my $id (sort keys %{$results->{$file}}) {
                next if $id eq 'headline';
                foreach my $r (sort @{$results->{$file}->{$id}->{'content'}} ){
                    $rss->add_item(title => $results->{$file}->{'headline'},
                       link  => "http://www.undemocracy.com/$web_link#$id",
                       description =>  $r
                       );
                }

            }
    
    }


    $dbh->do("insert into rsscache set term=?, content=?, generated=now()", undef, $search, $rss->as_string);
    print "Content-Type: text/xml\n\n";
    print $rss->as_string;
    
}



sub setup {
    open (CONFIG, "dbpasswords.py") || die " can't open pw file: $!";
    while (my $line =<CONFIG>) {
        #print $line;
        if ($line =~ m#^\s*\##) {
            # comment
        } elsif ($line =~ m#^\s*$#) {
            # empty line
       } elsif ($line =~ m#(\S+)[\s=]+'(\S+)'#) {
            $Config{$1}=$2;
        }

    }
    close (CONFIG) ;

    $search= param('search') || '';

    my $wtt_dsn = "DBI:mysql:$Config{'db_name'}:localhost"; # DSN connection string
    $dbh=DBI->connect($wtt_dsn, $Config{'db_user'}, $Config{'db_password'}, {RaiseError => 1});
}



sub process {
    my @yesterday= localtime(time - 60*60*24); 
    my $yesterday= join '', $yesterday[5]+1900 , '-' , $yesterday[4]+1 , '-' , $yesterday[3];
    #print "svn diff -r {$yesterday} ~/undata/html/\n";
    my $output= `echo t | /usr/bin/svn diff -r {$yesterday} /home/undemocracy/undata/html/ 2>&1`;
    # $output.= "echo t | /usr/bin/svn diff -r {$yesterday} /home/undemocracy/undata/html/ 2>&1";

#print "Content-Type: text/plain\n\n$output;";
#===================================================================
##--- /home/undemocracy/undata/html/S-PV-5941.html        (revision 0)
#+++ /home/undemocracy/undata/html/S-PV-5941.html        (revision 3902)
#@@ -0,0 +1,88 @@
#+<html>
#+<head>
#+<link href="unview.css" type="text/css" rel="stylesheet" media="all">
#+</head>
#+<body>
#+
#+<div class="heading" id="pg000-bk00">
#+       <span class="code">S-PV-5941</span> <span class="date">2008-07-23</span> <span class="time">10:00</span><span class="rosetime">10:15</sp
    my $counts;
    my ($id, $file)=('','');;
    foreach my $line (split /\n/, $output) {
        
        if ($line =~ m#^\+\+\+ (.*?\.html)\s#) {
            $file=basename($1, '.html');
            $id='';
        } elsif ($line =~ m#class="boldline-\w+"\s*id="([^"]+)">(.{1,50}.*?)\b#) {
            $counts->{$file}->{'headline'}=$2; 
            if ($search eq '') {
                $counts->{$file}->{$1}->{'count'}=1;
                $counts->{$file}->{$1}->{'content'}->[0] = '';
            }

        }


        next if ($search eq '');

        if ($line =~ m#^---#) {
            # skip it
        }elsif ($line =~ m#^@@#) {
            # skip it
        }elsif ($line=~ m#^ #) {
            if ($line =~m#id="([^"]+)"#) { $id= $1; }
        }elsif ($line =~ m#^\-#) {
            if ($line =~ m#$search#i) { $counts->{$file}->{$id}->{'count'}--; }
        }elsif ($line =~ m#^\+(.*)$#) {
            my $thisline;
            $thisline=$1;
            if ($line =~m#id="([^"]+)"#) { $id= $1; }
            if ($thisline =~ m#$search#io) { 
                $thisline=~ s#<[^>]*>##g;
                push @{$counts->{$file}->{$id}->{'content'}}, "$thisline\n";
                $counts->{$file}->{$id}->{'count'}++;
            }
        }

    }

    #print Dumper $search;
    #print Dumper $counts;
    

    return($counts);
}



