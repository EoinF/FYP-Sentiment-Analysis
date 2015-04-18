#!/usr/bin/env perl

use strict;
use warnings;

sub find_matches($);
sub find_matches_rec($\@\@);
sub find_word_seq_score(@);
sub get_word_stats($);
sub print_results($@);
sub Usage();

our(%DICT,$TOTAL);
{
my( $dict_file, $word_file ) = @ARGV;
($dict_file && $word_file) or die(Usage);

{
my $DICT;
($DICT, $TOTAL) = get_word_stats($dict_file);
%DICT = %$DICT;
}

{
open( my $WORDS, '<', $word_file ) or die "unable to open $word_file\n";

foreach my $word (<$WORDS>) {
chomp $word;
my $arr = find_matches($word);


local $_;
# Schwartzian Transform
my @sorted_arr =
map  { $_->[0] }
sort { $b->[1] <=> $a->[1] }
map  {
[ $_, find_word_seq_score(@$_) ]
}
@$arr;


print_results( $word, @sorted_arr );
}

close $WORDS;
}
}


sub find_matches($){
my( $string ) = @_;

my @found_parses;
my @words;
find_matches_rec( $string, @words, @found_parses );

return  @found_parses if wantarray;
return \@found_parses;
}

sub find_matches_rec($\@\@){
my( $string, $words_sofar, $found_parses ) = @_;
my $length = length $string;

unless( $length ){
push @$found_parses, $words_sofar;

return @$found_parses if wantarray;
return  $found_parses;
}

foreach my $i ( 2..$length ){
my $prefix = substr($string, 0, $i);
my $suffix = substr($string, $i, $length-$i);

if( exists $DICT{$prefix} ){
my @words = ( @$words_sofar, $prefix );
find_matches_rec( $suffix, @words, @$found_parses );
}
}

return @$found_parses if wantarray;
return  $found_parses;
}


## Just a simple joint probability
## assumes independence between words, which is obviously untrue
## that's why this is broken out -- feel free to add better brains
sub find_word_seq_score(@){
my( @words ) = @_;
local $_;

my $score = 1;
foreach ( @words ){
$score = $score * $DICT{$_} / $TOTAL;
}

return $score;
}

sub get_word_stats($){
my ($filename) = @_;

open(my $DICT, '<', $filename) or die "unable to open $filename\n";

local $/= undef;
local $_;
my %dict;
my $total = 0;

while ( <$DICT> ){
foreach ( split(/\b/, $_) ) {
$dict{$_} += 1;
$total++;
}
}

close $DICT;

return (\%dict, $total);
}

sub print_results($@){
#( 'word', [qw'test one'], [qw'test two'], ... )
my ($word,  @combos) = @_;
local $_;
my $possible = scalar @combos;

print "$word: $possible possibilities\n";
foreach (@combos) {
print ' -  ', join(' ', @$_), "\n";
}
print "\n";
}

sub Usage(){
return "$0 /path/to/dictionary /path/to/your_words";
}
