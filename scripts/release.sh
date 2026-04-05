#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SAMPLE_GRAPH="${REPO_ROOT}/tests/fixtures/sample_graph"
VERSION="$(awk -F'"' '/^version = / { print $2; exit }' "${REPO_ROOT}/pyproject.toml")"

export PYTHONPATH="${REPO_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/release.sh check
  ./scripts/release.sh smoke
  ./scripts/release.sh build
  ./scripts/release.sh all
  ./scripts/release.sh help

Commands:
  check   Run release checks (tests, CLI help, build module availability).
  smoke   Run representative JSON smoke tests against the sample graph.
  build   Clean local build artifacts and build sdist + wheel with --no-isolation.
  all     Run check, smoke, then build.
  help    Show this message.

Environment:
  PYTHON_BIN   Python executable to use. Default: python3

Notes:
  - This script only performs local release prep. It does not upload anything.
  - Built artifacts are written to dist/.
EOF
}

require_python() {
  if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    echo "error: python executable not found: ${PYTHON_BIN}" >&2
    exit 1
  fi
}

run_check() {
  require_python

  echo "==> Running tests"
  "${PYTHON_BIN}" -m pytest

  echo "==> Verifying CLI entrypoint"
  "${PYTHON_BIN}" -m logseq_cli.main --help >/dev/null

  echo "==> Verifying build module"
  "${PYTHON_BIN}" -m build --help >/dev/null
}

run_smoke() {
  require_python

  if [[ ! -d "${SAMPLE_GRAPH}" ]]; then
    echo "error: sample graph not found: ${SAMPLE_GRAPH}" >&2
    exit 1
  fi

  echo "==> Running smoke checks against ${SAMPLE_GRAPH}"
  "${PYTHON_BIN}" -m logseq_cli.main graph detect --graph "${SAMPLE_GRAPH}" --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main page list --graph "${SAMPLE_GRAPH}" --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main journal read --graph "${SAMPLE_GRAPH}" --date 2026-03-29 --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main search text OpenClaw --graph "${SAMPLE_GRAPH}" --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main search tags ops --graph "${SAMPLE_GRAPH}" --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main recall topic OpenClaw --graph "${SAMPLE_GRAPH}" --json >/dev/null
  "${PYTHON_BIN}" -m logseq_cli.main cards build weekly --graph "${SAMPLE_GRAPH}" --date 2026-03-29 --json >/dev/null
}

clean_build_outputs() {
  echo "==> Cleaning old build artifacts"
  rm -rf "${REPO_ROOT}/build" "${REPO_ROOT}/dist"
  find "${REPO_ROOT}" -maxdepth 1 -type d -name '*.egg-info' -exec rm -rf {} +
}

run_build() {
  require_python
  clean_build_outputs

  echo "==> Building release artifacts for ${VERSION}"
  (
    cd "${REPO_ROOT}"
    "${PYTHON_BIN}" -m build --sdist --wheel --no-isolation
  )

  echo "==> Built artifacts"
  find "${REPO_ROOT}/dist" -maxdepth 1 -type f | sort

  cat <<EOF

Next steps:
  Local install:
    ${PYTHON_BIN} -m pip install --upgrade ${REPO_ROOT}/dist/logseq_cli-${VERSION}-py3-none-any.whl

  Copy to another machine:
    - transfer dist/logseq_cli-${VERSION}-py3-none-any.whl
    - run: python3 -m pip install logseq_cli-${VERSION}-py3-none-any.whl

  Git release:
    git tag -a v${VERSION} -m "logseq-cli v${VERSION}"
    git push origin main
    git push origin v${VERSION}
EOF
}

main() {
  local command="${1:-all}"

  case "${command}" in
    check)
      run_check
      ;;
    smoke)
      run_smoke
      ;;
    build)
      run_build
      ;;
    all)
      run_check
      run_smoke
      run_build
      ;;
    help|-h|--help)
      usage
      ;;
    *)
      echo "error: unknown command: ${command}" >&2
      usage >&2
      exit 2
      ;;
  esac
}

main "$@"
