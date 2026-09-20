use std::env;
use std::io::{self, BufRead, Write};
use std::path::Path;

use fastbloom::{BloomFilter, DefaultHasher};

const MAGIC: &[u8] = b"FBF1";

fn load(path: &str) -> Option<BloomFilter<DefaultHasher>> {
    let bytes = std::fs::read(path).ok()?;
    if bytes.len() < 4 || &bytes[..4] != MAGIC {
        return None;
    }
    bincode::deserialize(&bytes[4..]).ok()
}

fn save(path: &str, f: &BloomFilter<DefaultHasher>) -> io::Result<()> {
    let mut out = Vec::with_capacity(4);
    out.extend_from_slice(MAGIC);
    bincode::serialize_into(&mut out, f).expect("serialize");
    std::fs::write(path, out)
}

fn usage() {
    eprintln!(
        "usage: bloomfast FILTER_PATH [--projected N] [--fp P] [--seed S] [--check]\n\
         reads candidate strings (one per line) from stdin\n\
         default: prints only unseen lines, inserts them into FILTER_PATH\n\
         --check: writes [dup] or [new] per line to stdout, mutates nothing\n\
         --projected N: expected element count (default 5000000)\n\
         --fp P: max false positive probability 0<P<1 (default 0.000001)\n\
         --seed S: fixed hasher seed (default 0xA5A5A5A5)"
    );
}

fn main() {
    let mut path: Option<String> = None;
    let mut projected: u64 = 5_000_000;
    let mut fp: f64 = 0.000001;
    let mut seed: u64 = 0xA5A5A5A5;
    let mut check = false;

    let args: Vec<String> = env::args().skip(1).collect();
    let mut i = 0;
    while i < args.len() {
        match args[i].as_str() {
            "--projected" => {
                projected = args.get(i + 1).and_then(|s| s.parse().ok()).expect("--projected N");
                i += 2;
            }
            "--fp" => {
                fp = args.get(i + 1).and_then(|s| s.parse().ok()).expect("--fp P");
                i += 2;
            }
            "--seed" => {
                seed = args.get(i + 1).and_then(|s| s.parse().ok()).expect("--seed S");
                i += 2;
            }
            "--check" => {
                check = true;
                i += 1;
            }
            a if path.is_none() => {
                path = Some(a.to_string());
                i += 1;
            }
            a => {
                eprintln!("unknown arg: {a}");
                usage();
                std::process::exit(2);
            }
        }
    }
    let Some(path) = path else {
        usage();
        std::process::exit(2);
    };

    let mut filter = if Path::new(&path).exists() {
        load(&path).unwrap_or_else(|| {
            eprintln!("corrupt filter file: {path}");
            std::process::exit(3)
        })
    } else {
        let mut sb = [0u8; 16];
        sb[..8].copy_from_slice(&seed.to_le_bytes());
        sb[8..].copy_from_slice(&0xA5A5A5A5A5A5A5A5u64.to_le_bytes());
        let hasher = DefaultHasher::seeded(&sb);
        BloomFilter::with_false_pos(fp)
            .hasher(hasher)
            .expected_items(projected as usize)
    };

    let stdin = io::stdin();
    let stdout = io::stdout();
    let mut out = stdout.lock();
    let mut line = String::new();
    let mut seen: u64 = 0;
    let mut inserted: u64 = 0;
    let mut rd = stdin.lock();
    loop {
        line.clear();
        if rd.read_line(&mut line).expect("read_line") == 0 {
            break;
        }
        let trimmed = line.trim_end_matches(['\n', '\r']);
        if trimmed.is_empty() && line.is_empty() {
            continue;
        }
        if check {
            if filter.contains(trimmed) {
                writeln!(out, "[dup]\t{trimmed}").expect("write");
            } else {
                writeln!(out, "[new]\t{trimmed}").expect("write");
            }
            continue;
        }
        if !filter.contains(trimmed) {
            writeln!(out, "{trimmed}").expect("write");
            filter.insert(trimmed);
            inserted += 1;
        }
        seen += 1;
    }

    if !check {
        if save(&path, &filter).is_err() {
            eprintln!("write failed: {path}");
            std::process::exit(3);
        }
        eprintln!("lines={seen} new={inserted} fp={fp} bits={}", filter.num_bits());
    }
}