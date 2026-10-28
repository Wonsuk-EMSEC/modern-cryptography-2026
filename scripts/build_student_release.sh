#!/usr/bin/env bash
# Build the Lab01–Lab03 student archive. Target images are distributed separately.
set -euo pipefail

usage() {
    echo "usage: $0 OUTPUT_DIRECTORY" >&2
}

if [[ $# -ne 1 || -z "$1" || "$1" == -* ]]; then
    usage
    exit 2
fi
release_dir=$1

if [[ -e "$release_dir" ]]; then
    echo "output path already exists: $release_dir" >&2
    exit 2
fi

repo_root=$(git rev-parse --show-toplevel)
staging_dir=$(mktemp -d)
trap 'rm -rf "$staging_dir"' EXIT
mkdir "$staging_dir/source"

required_files=(
    labs/lab01/part1_hashing/data/flag_challenge.json
    labs/lab01/part2_dictionary_attack/data/flag_challenge.json
    labs/lab01/part3_password_kdfs/data/flag_challenge.json
    labs/lab01/part4_system_hashes/data/flag_challenge.json
    labs/lab01/part5_wpa2/data/flag_challenge.json
    labs/lab01/part5_wpa2/data/wpa2/lab01-handshake.pcap
    labs/lab02/part1_des_bruteforce/data/known_plaintext.bin
    labs/lab02/part1_des_bruteforce/data/encrypted_flag.bin
    labs/lab02/part2_double_des_mitm/data/known_pairs.json
    labs/lab02/part3_aes_cbc_pkcs7/data/encrypted_flag.bin
    labs/lab02/part5_padding_oracle/data/ciphertext.hex
    labs/lab02/part7_aes_cpa/data/plaintexts.npy
    labs/lab02/part7_aes_cpa/data/traces.npy
    labs/lab02/part7_aes_cpa/data/secret_ciphertext.bin
    labs/lab03/data_manifest.json
    labs/lab03/part02/data/confidential_report.enc
    labs/lab03/part03/data/primes2048.txt
    labs/lab03/part03/data/primes3072.txt
    labs/lab03/part07/data/trusted_public.pem
    labs/lab03/part07/data/update.sig
)
for required_file in "${required_files[@]}"; do
    if [[ ! -f "$repo_root/$required_file" ]]; then
        echo "missing course data file: $required_file" >&2
        echo "check the instructor Lab01/Lab02/Lab03 preparation steps before packaging" >&2
        exit 2
    fi
done

# This manifest is intentionally file-level rather than directory-level. It
# prevents stray files under either lab from becoming part of a student bundle.
student_paths=(
    .devcontainer/devcontainer.json
    README.md
    CONTRIBUTING.md
    scripts/check_translations.py
    en/.translation-status.json
    en/README.md
    en/CONTRIBUTING.md
    en/docker/README.md
    en/docker/lab01-ssh-target/README.md
    en/docker/lab02-target/README.md
    en/labs/lab01/README.md
    en/labs/lab01/common/README.md
    en/labs/lab01/part1_hashing/README.md
    en/labs/lab01/part1_hashing/data/README.md
    en/labs/lab01/part2_dictionary_attack/README.md
    en/labs/lab01/part2_dictionary_attack/data/README.md
    en/labs/lab01/part3_password_kdfs/README.md
    en/labs/lab01/part3_password_kdfs/data/README.md
    en/labs/lab01/part4_system_hashes/README.md
    en/labs/lab01/part4_system_hashes/data/README.md
    en/labs/lab01/part5_wpa2/README.md
    en/labs/lab01/part5_wpa2/CAPTURE_WORKSHEET.md
    en/labs/lab01/part5_wpa2/data/README.md
    en/labs/lab01/part5_wpa2/data/wpa2/PLACE_PCAP_HERE.md
    en/labs/lab02/README.md
    en/labs/lab02/part1_des_bruteforce/README.md
    en/labs/lab02/part2_double_des_mitm/README.md
    en/labs/lab02/part3_aes_cbc_pkcs7/README.md
    en/labs/lab02/part4_cbc_bit_flipping/README.md
    en/labs/lab02/part5_padding_oracle/README.md
    en/labs/lab02/part6_mte_vs_etm/README.md
    en/labs/lab02/part7_aes_cpa/README.md
    docker/README.md
    docker/Dockerfile
    docker/compose.yml
    docker/lab01-ssh-target/Dockerfile
    docker/lab01-ssh-target/README.md
    docker/lab01-ssh-target/sshd_config
    docker/lab02-target/Dockerfile
    docker/lab02-target/README.md
    labs/__init__.py
    labs/lab01/LICENSE
    labs/lab01/Makefile
    labs/lab01/README.md
    labs/lab01/common/README.md
    labs/lab01/common/__init__.py
    labs/lab01/common/flags.py
    labs/lab01/common/samples/__init__.py
    labs/lab01/common/samples/flag_unlock_demo.py
    labs/lab01/common/samples/public_flag_challenge.json
    labs/lab01/part1_hashing/README.md
    labs/lab01/part1_hashing/data/README.md
    labs/lab01/part1_hashing/data/flag_challenge.json
    labs/lab01/part1_hashing/data/md5_collision_a.bin
    labs/lab01/part1_hashing/data/md5_collision_b.bin
    labs/lab01/part1_hashing/hash_password.py
    labs/lab01/part1_hashing/salted_hash.py
    labs/lab01/part1_hashing/samples/flag_unlock_demo.py
    labs/lab01/part1_hashing/samples/hash_bytes_demo.py
    labs/lab01/part1_hashing/samples/salt_bytes_demo.py
    labs/lab01/part1_hashing/test_hashing.py
    labs/lab01/part2_dictionary_attack/README.md
    labs/lab01/part2_dictionary_attack/data/README.md
    labs/lab01/part2_dictionary_attack/data/flag_challenge.json
    labs/lab01/part2_dictionary_attack/data/ssh-lab-wordlist.txt
    labs/lab01/part2_dictionary_attack/samples/flag_unlock_demo.py
    labs/lab01/part2_dictionary_attack/samples/ssh_api_demo.py
    labs/lab01/part2_dictionary_attack/ssh_dictionary_attack.py
    labs/lab01/part2_dictionary_attack/test_ssh_dictionary_attack.py
    labs/lab01/part3_password_kdfs/README.md
    labs/lab01/part3_password_kdfs/compare_cost.py
    labs/lab01/part3_password_kdfs/crack_salted.py
    labs/lab01/part3_password_kdfs/crack_unsalted.py
    labs/lab01/part3_password_kdfs/data/README.md
    labs/lab01/part3_password_kdfs/data/flag_challenge.json
    labs/lab01/part3_password_kdfs/data/lab01-small.txt
    labs/lab01/part3_password_kdfs/data/passwords.txt
    labs/lab01/part3_password_kdfs/data/salted_hashes.csv
    labs/lab01/part3_password_kdfs/data/sha256_targets.txt
    labs/lab01/part3_password_kdfs/data/unsalted_hashes.csv
    labs/lab01/part3_password_kdfs/samples/benchmark_kdfs.py
    labs/lab01/part3_password_kdfs/samples/csv_hash_demo.py
    labs/lab01/part3_password_kdfs/samples/flag_unlock_demo.py
    labs/lab01/part3_password_kdfs/samples/register_login_demo.py
    labs/lab01/part3_password_kdfs/test_dictionary_cost.py
    labs/lab01/part4_system_hashes/README.md
    labs/lab01/part4_system_hashes/build_precomputation_table.py
    labs/lab01/part4_system_hashes/build_rainbow_table.py
    labs/lab01/part4_system_hashes/compare_table_attacks.py
    labs/lab01/part4_system_hashes/data/README.md
    labs/lab01/part4_system_hashes/data/flag_challenge.json
    labs/lab01/part4_system_hashes/data/lab01-small.txt
    labs/lab01/part4_system_hashes/data/linux_hashes.txt
    labs/lab01/part4_system_hashes/data/rainbow_config.json
    labs/lab01/part4_system_hashes/data/rainbow_lab_config.json
    labs/lab01/part4_system_hashes/data/rainbow_password_database.csv
    labs/lab01/part4_system_hashes/data/rainbow_targets.txt
    labs/lab01/part4_system_hashes/data/salted_targets.json
    labs/lab01/part4_system_hashes/samples/analyze_shadow_hash.py
    labs/lab01/part4_system_hashes/samples/flag_unlock_demo.py
    labs/lab01/part4_system_hashes/samples/table_io_demo.py
    labs/lab01/part4_system_hashes/table_common.py
    labs/lab01/part4_system_hashes/test_table_attacks.py
    labs/lab01/part5_wpa2/CAPTURE_WORKSHEET.md
    labs/lab01/part5_wpa2/README.md
    labs/lab01/part5_wpa2/data/README.md
    labs/lab01/part5_wpa2/data/flag_challenge.json
    labs/lab01/part5_wpa2/data/wpa2/PLACE_PCAP_HERE.md
    labs/lab01/part5_wpa2/data/wpa2/lab01-handshake.pcap
    labs/lab01/part5_wpa2/data/wpa2/lab01-pcap-wordlist.txt
    labs/lab01/part5_wpa2/data/wpa2_capture.json
    labs/lab01/part5_wpa2/data/wpa2_passwords.txt
    labs/lab01/part5_wpa2/samples/bytes_hmac_demo.py
    labs/lab01/part5_wpa2/samples/explain_handshake.py
    labs/lab01/part5_wpa2/samples/flag_unlock_demo.py
    labs/lab01/part5_wpa2/test_wpa2_workflow.py
    labs/lab01/part5_wpa2/verify_candidate.py
    labs/lab01/requirements.txt
    labs/lab01/tests/__init__.py
    labs/lab01/tests/test_md5_collision.py
    labs/lab01/tests/test_password_authentication.py
    labs/lab02/Makefile
    labs/lab02/README.md
    labs/lab02/__init__.py
    labs/lab02/common/__init__.py
    labs/lab02/common/des.py
    labs/lab02/common/service_client.py
    labs/lab02/part1_des_bruteforce/README.md
    labs/lab02/part1_des_bruteforce/samples/des_roundtrip.py
    labs/lab02/part1_des_bruteforce/samples/data_loading.py
    labs/lab02/part1_des_bruteforce/des_bruteforce.py
    labs/lab02/part1_des_bruteforce/data/encrypted_flag.bin
    labs/lab02/part1_des_bruteforce/data/known_ciphertext.bin
    labs/lab02/part1_des_bruteforce/data/known_plaintext.bin
    labs/lab02/part1_des_bruteforce/data/parameters.json
    labs/lab02/part2_double_des_mitm/README.md
    labs/lab02/part2_double_des_mitm/samples/double_des_roundtrip.py
    labs/lab02/part2_double_des_mitm/samples/data_loading.py
    labs/lab02/part2_double_des_mitm/double_des_mitm.py
    labs/lab02/part2_double_des_mitm/data/encrypted_flag.bin
    labs/lab02/part2_double_des_mitm/data/known_pairs.json
    labs/lab02/part3_aes_cbc_pkcs7/README.md
    labs/lab02/part3_aes_cbc_pkcs7/samples/aes_cbc_demo.py
    labs/lab02/part3_aes_cbc_pkcs7/aes_cbc_pkcs7.py
    labs/lab02/part3_aes_cbc_pkcs7/data/encrypted_flag.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/iv.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/key.bin
    labs/lab02/part3_aes_cbc_pkcs7/data/nist_cbc_vector.json
    labs/lab02/part4_cbc_bit_flipping/README.md
    labs/lab02/part4_cbc_bit_flipping/client.py
    labs/lab02/part4_cbc_bit_flipping/samples/cbc_token_demo.py
    labs/lab02/part4_cbc_bit_flipping/cbc_bit_flipping.py
    labs/lab02/part5_padding_oracle/README.md
    labs/lab02/part5_padding_oracle/oracle_client.py
    labs/lab02/part5_padding_oracle/samples/padding_demo.py
    labs/lab02/part5_padding_oracle/padding_oracle.py
    labs/lab02/part5_padding_oracle/data/ciphertext.hex
    labs/lab02/part6_mte_vs_etm/README.md
    labs/lab02/part6_mte_vs_etm/client.py
    labs/lab02/part6_mte_vs_etm/samples/service_demo.py
    labs/lab02/part6_mte_vs_etm/mte_vs_etm.py
    labs/lab02/part7_aes_cpa/README.md
    labs/lab02/part7_aes_cpa/__init__.py
    labs/lab02/part7_aes_cpa/aes.py
    labs/lab02/part7_aes_cpa/cpa.py
    labs/lab02/part7_aes_cpa/model.py
    labs/lab02/part7_aes_cpa/samples/power_trace_demo.py
    labs/lab02/part7_aes_cpa/samples/model_demo.py
    labs/lab02/part7_aes_cpa/aes_cpa.py
    labs/lab02/part7_aes_cpa/trace_count_experiment.py
    labs/lab02/part7_aes_cpa/data/plaintexts.npy
    labs/lab02/part7_aes_cpa/data/secret_ciphertext.bin
    labs/lab02/part7_aes_cpa/data/traces.npy
    labs/lab02/tests/__init__.py
    labs/lab02/tests/_load_impl.py
    labs/lab02/tests/test_exercises.py
    labs/lab02/tests/test_des_primitives.py
    labs/lab02/tests/test_service_interface.py
    docker/lab03-target/Dockerfile
    docker/lab03-target/README.md
    en/docker/lab03-target/README.md
    en/labs/lab03/README.md
    en/labs/lab03/REPORT_TEMPLATE.md
    en/labs/lab03/part01/README.md
    en/labs/lab03/part02/README.md
    en/labs/lab03/part03/README.md
    en/labs/lab03/part04/README.md
    en/labs/lab03/part05/README.md
    en/labs/lab03/part06/README.md
    en/labs/lab03/part07/README.md
    en/labs/lab03/part08/README.md
    labs/lab03/Makefile
    labs/lab03/README.md
    labs/lab03/REPORT_TEMPLATE.md
    labs/lab03/__init__.py
    labs/lab03/check.py
    labs/lab03/common/__init__.py
    labs/lab03/common/service_client.py
    labs/lab03/data_manifest.json
    labs/lab03/part01/README.md
    labs/lab03/part01/data/challenge.json
    labs/lab03/part01/starter/math_challenges.py
    labs/lab03/part01/starter/prime64.py
    labs/lab03/part01/tests/check.py
    labs/lab03/part02/README.md
    labs/lab03/part02/data/challenge.json
    labs/lab03/part02/data/confidential_report.enc
    labs/lab03/part02/starter/pdf_encryption.c
    labs/lab03/part02/starter/recover.py
    labs/lab03/part02/starter/secure_random.c
    labs/lab03/part02/tests/check.py
    labs/lab03/part02/tests/rng_driver.c
    labs/lab03/part03/README.md
    labs/lab03/part03/data/primes2048.txt
    labs/lab03/part03/data/primes3072.txt
    labs/lab03/part03/starter/rsa_engine.c
    labs/lab03/part03/starter/rsa_engine.h
    labs/lab03/part03/starter/rsa_io.c
    labs/lab03/part03/tests/check.py
    labs/lab03/part03/tests/driver.c
    labs/lab03/part04/README.md
    labs/lab03/part04/data/challenge.json
    labs/lab03/part04/starter/recover.py
    labs/lab03/part04/tests/check.py
    labs/lab03/part05/README.md
    labs/lab03/part05/data/challenge.json
    labs/lab03/part05/starter/recover.py
    labs/lab03/part05/tests/check.py
    labs/lab03/part06/README.md
    labs/lab03/part06/data/protocol.json
    labs/lab03/part06/starter/attack.py
    labs/lab03/part06/tests/check.py
    labs/lab03/part07/README.md
    labs/lab03/part07/data/trusted_public.pem
    labs/lab03/part07/data/update.bin
    labs/lab03/part07/data/update.sig
    labs/lab03/part07/starter/pss.c
    labs/lab03/part07/starter/pss.h
    labs/lab03/part07/starter/update.c
    labs/lab03/part07/starter/update_vulnerable.c
    labs/lab03/part07/tests/check.py
    labs/lab03/part07/tests/driver.c
    labs/lab03/part08/README.md
    labs/lab03/part08/data/protocol.json
    labs/lab03/part08/starter/attack.py
    labs/lab03/part08/tests/check.py
    labs/lab03/tests/test_materials.py
)
for student_path in "${student_paths[@]}"; do
    if [[ ! -e "$repo_root/$student_path" ]]; then
        echo "missing student-release path: $student_path" >&2
        exit 2
    fi
done

tar -C "$repo_root" -cf - "${student_paths[@]}" | tar -C "$staging_dir/source" -xf -

tar -C "$staging_dir/source" -czf "$staging_dir/modern-cryptography-2026-student.tar.gz" .

mkdir -p "$release_dir"
mv "$staging_dir/modern-cryptography-2026-student.tar.gz" "$release_dir/"
echo "created $release_dir/modern-cryptography-2026-student.tar.gz"
