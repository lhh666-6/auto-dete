use File::Basename qw(basename);
use File::Copy qw(copy);

$out_dir = 'out';
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

# Keep build intermediates under out/ while placing the final PDF beside main.tex.
END {
    if (defined $out_dir) {
        for my $pdf (glob("$out_dir/*.pdf")) {
            copy($pdf, basename($pdf));
        }
    }
}
