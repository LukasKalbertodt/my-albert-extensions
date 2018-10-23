use std::{
    error::Error,
    fs,
    io::Write,
};

fn main() -> Result<(), Box<dyn Error>> {
    let contents = fs::read_to_string("NamesList.txt")?;
    let mut out_file = fs::File::create("symbols.txt").unwrap();

    contents.lines()
        // Filter out all comments, explanations, and all that stuff
        .filter(|line| {
            !(line.starts_with('@') || line.starts_with(';') || line.starts_with('\t'))
        })

        // Some characters are special, like `<control>` or `<not a
        // character>`. We don't want those.
        .filter(|line| !line.ends_with('>'))

        // Split by <tab> character to get the unicode value and the name
        .map(|line| {
            let mut it = line.split('\t');

            // Parse unicode number into character
            let num = it.next().unwrap();
            let num = u32::from_str_radix(num, 16).unwrap();
            let c = std::char::from_u32(num).unwrap();

            // Convert the name into lowercase. Will make searching faster.
            let name = it.next().unwrap();
            let name = name.to_ascii_lowercase();

            // Make sure our parsing assumptions are correct
            assert!(it.next().is_none());
            assert!(name.is_ascii());

            (c, name)
        })

        // Write everything into the new file
        .for_each(|(c, name)| writeln!(out_file, "{}\t{}", c, name).unwrap());

    Ok(())
}
