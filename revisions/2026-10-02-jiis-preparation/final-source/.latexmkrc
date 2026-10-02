$pdf_mode = 1;
$out_dir = "out";
END { use File::Copy; for my $name ("main", "ESM_1") { copy("out/$name.pdf", "$name.pdf") if -f "out/$name.pdf"; } }
