$pdf_mode = 1;
$interaction = 'nonstopmode';
$out_dir = 'out';
$aux_dir = 'out';
$max_repeat = 5;

END {
    for my $name ('main_anonymous', 'title_page', 'supplementary') {
        my $source = "$out_dir/$name.pdf";
        if (-e $source) {
            system("copy /Y \"$source\" \"$name.pdf\" >NUL");
        }
    }
}
