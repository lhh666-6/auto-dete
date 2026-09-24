use File::Copy qw(copy);
$out_dir = 'out';
END {
    copy('out/manuscript.pdf', 'manuscript.pdf') if -e 'out/manuscript.pdf';
}
