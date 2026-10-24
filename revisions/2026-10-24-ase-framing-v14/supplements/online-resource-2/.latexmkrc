$pdf_mode = 1;
$out_dir = 'out';
$interaction = 'nonstopmode';

END {
    require File::Copy;
    if ($? == 0 && -f 'out/main.pdf') {
        File::Copy::copy('out/main.pdf', 'main.pdf') or warn "PDF copy failed: $!";
    }
}
