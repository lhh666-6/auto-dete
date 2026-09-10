use Cwd qw(getcwd);
use File::Basename qw(basename);
use File::Copy qw(copy);
use File::Path qw(make_path);

$out_dir = 'out';
$pdf_mode = 1;
$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

# bibtex runs with the output directory as its working directory; mirror the
# database there so a clean checkout builds without external configuration.
make_path($out_dir);
copy('filtered.bib', "$out_dir/filtered.bib") if -f 'filtered.bib';

# Keep build intermediates under out/ while placing the final PDF beside main.tex.
END {
    if (defined $out_dir) {
        for my $pdf (glob("$out_dir/*.pdf")) {
            copy($pdf, basename($pdf));
        }
    }
}
