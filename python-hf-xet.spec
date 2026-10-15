%undefine _debugsource_packages
%define oname hf_xet

# Recreate the vendor archive after a version bump:
#   tar xf hf_xet-VERSION.tar.gz
#   cd hf_xet-VERSION/hf_xet
#   cargo vendor --locked ../vendor
#   cd ..
#   tar cJf python-hf-xet-VERSION-vendor.tar.xz vendor
#   abb store python-hf-xet-VERSION-vendor.tar.xz

Name:		python-hf-xet
Version:	1.7.0
Release:	1
Summary:	Fast transfer of large files with the Hugging Face Hub
License:	Apache-2.0
Group:		Development/Python
URL:		https://pypi.org/project/hf-xet/
Source0:	https://files.pythonhosted.org/packages/source/h/hf-xet/hf_xet-%{version}.tar.gz
Source1:	%{name}-%{version}-vendor.tar.xz

BuildSystem:	python
BuildRequires:	cargo
BuildRequires:	cmake
BuildRequires:	pkgconfig(python3)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	python%{pyver}dist(wheel)

%description
hf-xet enables huggingface_hub to use Xet storage for uploading and
downloading from the Hugging Face Hub. Xet storage provides chunk-based
deduplication, efficient storage and retrieval with local disk caching,
and backwards compatibility with Git LFS.

%prep -a
# Extract vendored crate tarball. rust-packaging pulls python-rust2rpm,
# which still requires Python 3.14.
tar xf %{SOURCE1}
rm -f Cargo.toml.orig hf_xet/Cargo.toml.orig
mkdir -p .cargo
cat > .cargo/config.toml << EOF
[net]
offline = true

[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "$PWD/vendor"
EOF
# maturin builds from hf_xet/
ln -sfn ../.cargo hf_xet/.cargo

%build -p
export CARGO_HOME=$PWD/.cargo
export CARGO_NET_OFFLINE=true
# Cargo.toml sets lto = true. Combined with the distro
# -C linker-plugin-lto, rustc aborts in LLVM on __rust_alloc.
export CARGO_PROFILE_RELEASE_LTO=off

%build -a
# hf_xet is excluded from the root workspace (and the sdist omits git_xet),
# so generate the license list from the crate that maturin actually builds.
pushd hf_xet
cargo tree --locked --offline --edges no-build,no-dev,no-proc-macro \
	--prefix none --format '{l}: {p}' \
	| sed -e "s: ($(pwd)[^)]*)::g" -e 's: / :/:g' -e 's:/: OR :g' \
	| sort -u > ../LICENSES.dependencies
popd

%files
%doc README.md
%license LICENSE LICENSES.dependencies
%{python_sitearch}/%{oname}
%{python_sitearch}/%{oname}-%{version}.dist-info
