$pdf_mode = 1;
$out_dir = 'out';
END { use File::Copy; copy("out/main.pdf", "main.pdf") if -f "out/main.pdf"; }
