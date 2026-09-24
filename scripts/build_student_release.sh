#!/usr/bin/env bash
# Build the Lab02 student source archive and, optionally, a separate target image.
set -euo pipefail

usage() {
    echo "usage: $0 OUTPUT_DIRECTORY [--include-target-image]" >&2
}

release_dir=
include_target_image=false
for argument in "$@"; do
    case "$argument" in
        --include-target-image)
            if "$include_target_image"; then
                usage
                exit 2
            fi
            include_target_image=true
            ;;
        -*)
            usage
            exit 2
            ;;
        *)
            if [[ -n "$release_dir" ]]; then
                usage
                exit 2
            fi
            release_dir=$argument
            ;;
    esac
done
if [[ -z "$release_dir" ]]; then
    usage
    exit 2
fi

if [[ -e "$release_dir" ]]; then
    echo "output path already exists: $release_dir" >&2
    exit 2
fi

repo_root=$(git rev-parse --show-toplevel)
staging_dir=$(mktemp -d)
trap 'rm -rf "$staging_dir"' EXIT
mkdir "$staging_dir/source"

required_files=(
    labs/lab02/part1_des_bruteforce/data/known_plaintext.bin
    labs/lab02/part1_des_bruteforce/data/encrypted_flag.bin
    labs/lab02/part2_double_des_mitm/data/known_pairs.json
    labs/lab02/part3_aes_cbc_pkcs7/data/encrypted_flag.bin
    labs/lab02/part5_padding_oracle/data/ciphertext.hex
    labs/lab02/part7_aes_cpa/data/plaintexts.npy
    labs/lab02/part7_aes_cpa/data/traces.npy
    labs/lab02/part7_aes_cpa/data/secret_ciphertext.bin
)
for required_file in "${required_files[@]}"; do
    if [[ ! -f "$repo_root/$required_file" ]]; then
        echo "missing generated Lab02 file: $required_file" >&2
        echo "run the instructor data generator before packaging" >&2
        exit 2
    fi
done

# This manifest is intentionally file-level rather than directory-level. It
# prevents a stray file under labs/lab02 from becoming part of a student bundle.
student_paths=(
    README.md
    docker/README.md
    docker/Dockerfile
    docker/compose.yml
    docker/lab01-ssh-target/Dockerfile
    docker/lab01-ssh-target/sshd_config
    docker/lab02-target/Dockerfile
    docker/lab02-target/README.md
    labs/lab02/Makefile
    labs/lab02/README.md
    labs/lab02/__init__.py
    labs/lab02/common/__init__.py
    labs/lab02/common/des.py
    labs/lab02/common/service_client.py
    labs/lab02/part1_des_bruteforce/README.md
    labs/lab02/part1_des_bruteforce/starter.py
    labs/lab02/part1_des_bruteforce/data/encrypted_flag.bin
    labs/lab02/part1_des_bruteforce/data/known_ciphertext.bin
    labs/lab02/part1_des_bruteforce/data/known_plaintext.bin
    labs/lab02/part1_des_bruteforce/data/parameters.json
    labs/lab02/part2_double_des_mitm/README.md
    labs/lab02/part2_double_des_mitm/starter.py
    labs/lab02/part2_double_des_mitm/data/encrypted_flag.bin
    labs/lab02/part2_double_des_mitm/data/known_pairs.json
    labs/lab02/part3_aes_cbc_pkcs7/README.md
    labs/lab02/part3_aes_cbc_pkcs7/starter.py
    labs/lab02/part3_aes_cbc_pkcs7/data/encrypted_flag.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/iv.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/key.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/nist_cbc_vector.json
    labs/lab02/part4_cbc_bit_flipping/README.md
    labs/lab02/part4_cbc_bit_flipping/client.py
    labs/lab02/part4_cbc_bit_flipping/starter.py
    labs/lab02/part5_padding_oracle/README.md
    labs/lab02/part5_padding_oracle/oracle_client.py
    labs/lab02/part5_padding_oracle/starter.py
    labs/lab02/part5_padding_oracle/data/ciphertext.hex
    labs/lab02/part6_mte_vs_etm/README.md
    labs/lab02/part6_mte_vs_etm/client.py
    labs/lab02/part6_mte_vs_etm/starter.py
    labs/lab02/part7_aes_cpa/README.md
    labs/lab02/part7_aes_cpa/__init__.py
    labs/lab02/part7_aes_cpa/aes.py
    labs/lab02/part7_aes_cpa/cpa.py
    labs/lab02/part7_aes_cpa/model.py
    labs/lab02/part7_aes_cpa/starter.py
    labs/lab02/part7_aes_cpa/trace_count_experiment.py
    labs/lab02/part7_aes_cpa/data/plaintexts.npy
    labs/lab02/part7_aes_cpa/data/secret_ciphertext.bin
    labs/lab02/part7_aes_cpa/data/traces.npy
    labs/lab02/report/LAB_REPORT_TEMPLATE.md
    labs/lab02/tests/__init__.py
    labs/lab02/tests/_load_impl.py
    labs/lab02/tests/test_completed_starters.py
    labs/lab02/tests/test_des_primitives.py
    labs/lab02/tests/test_service_interface.py
)
for student_path in "${student_paths[@]}"; do
    if [[ ! -e "$repo_root/$student_path" ]]; then
        echo "missing student-release path: $student_path" >&2
        exit 2
    fi
done

tar -C "$repo_root" -cf - "${student_paths[@]}" | tar -C "$staging_dir/source" -xf -

tar -C "$staging_dir/source" -czf "$staging_dir/modern-cryptography-2026-student.tar.gz" .

if "$include_target_image"; then
    # Staff build the current course image first. Check that the distributed
    # ciphertexts and the private target secrets come from the same generator.
    docker compose -f "$repo_root/docker/compose.yml" run --rm course \
        python3 -m instructor.lab02.generators.build_data --check
    docker build -f "$repo_root/docker/lab02-target/Dockerfile" \
        -t modern-cryptography-2026-lab02-target "$repo_root"
    docker save modern-cryptography-2026-lab02-target \
        | gzip > "$staging_dir/lab02-target-image.tar.gz"
fi

mkdir -p "$release_dir"
mv "$staging_dir/modern-cryptography-2026-student.tar.gz" "$release_dir/"
echo "created $release_dir/modern-cryptography-2026-student.tar.gz"
if "$include_target_image"; then
    mv "$staging_dir/lab02-target-image.tar.gz" "$release_dir/"
    echo "created $release_dir/lab02-target-image.tar.gz"
fi
