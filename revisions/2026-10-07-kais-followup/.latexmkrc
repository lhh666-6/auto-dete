$out_dir = 'out';
$pdflatex = 'pdflatex -disable-installer %O %S';
END {
    require File::Copy;
    for my $pdf (glob 'out/*.pdf') {
        File::Copy::copy($pdf, '.');
    }
}
