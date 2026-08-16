$out_dir = 'out';

# Keep build artefacts in out/ and copy the final PDF beside main.tex.
END {
    if (defined $out_dir) {
        if ($^O eq 'MSWin32') {
            system("copy /Y out\\*.pdf . >NUL 2>NUL");
        } else {
            system("cp $out_dir/*.pdf . 2>/dev/null");
        }
    }
}
