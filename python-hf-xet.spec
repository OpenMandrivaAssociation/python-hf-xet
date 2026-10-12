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
BuildRequires:	pkgconfig(python)
BuildRequires:	python%{pyver}dist(maturin)
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	rust-packaging

%description
hf-xet enables huggingface_hub to use Xet storage for uploading and
downloading from the Hugging Face Hub. Xet storage provides chunk-based
deduplication, efficient storage and retrieval with local disk caching,
and backwards compatibility with Git LFS.

%prep -a
# Extract vendored crate tarball
tar xf %{SOURCE1}
# Point cargo at the vendored crates (offline builds)
%cargo_prep -v vendor
# cargo_prep writes a CWD-relative path; maturin/cargo also run from hf_xet/
sed -i "s#directory = \"vendor\"#directory = \"$PWD/vendor\"#" .cargo/config.toml

%build -p
export CARGO_HOME=$PWD/.cargo
export CARGO_NET_OFFLINE=true

%build -a
# hf_xet is excluded from the root workspace (and the sdist omits git_xet),
# so generate the license list from the crate that maturin actually builds.
ln -sfn ../.cargo hf_xet/.cargo
pushd hf_xet
%cargo_license_summary
%{cargo_license} > ../LICENSES.dependencies
popd

%files
%doc README.md
%license LICENSE LICENSES.dependencies
%{python_sitearch}/%{oname}
%{python_sitearch}/%{oname}-%{version}.dist-info
