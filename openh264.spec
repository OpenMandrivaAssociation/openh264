%define major 4
%define libname	%mklibname openh264 %{major}
%define devname	%mklibname -d openh264

Name:         	openh264
Summary:      	Open Source H.264 Codec
URL:          	http://www.openh264.org/
Group:        	System/Libraries
License:      	BSD
Version:      	1.8.0
Release:        1
Source0:	https://github.com/cisco/openh264/archive/v%{version}.tar.gz
Source1:	openh264.rpmlintrc
Source2:	https://github.com/mozilla/gmp-api/archive/master.zip
BuildRequires: 	nasm git unzip

%description
OpenH264 is a codec library which supports H.264 encoding and decoding.
It is suitable for use in real time applications such as WebRTC.

%package -n	%{libname}
Summary:	Open Source H.264 Codec
Group:		System/Libraries

%description -n	%{libname}
OpenH264 is a codec library which supports H.264 encoding and decoding.
It is suitable for use in real time applications such as WebRTC.

%package -n %{devname}
Summary: Development files for %{name}
Requires: %{libname} = %{EVRD}

%description -n %{devname}
Header files and libraries for the package %{name}.

%package     -n mozilla-openh264
Summary:        H.264 codec support for Mozilla browsers
Requires:       %{libname} = %{EVRD}

%description -n mozilla-openh264
The mozilla-openh264 package contains a H.264 codec plugin for Mozilla
browsers.

%prep
%setup -q

#------------------------|
# Api for mozilla plugin
# Extract gmp-api archive
unzip %{S:2}
mv gmp-api-master gmp-api
#------------------------|

%build

# Update the makefile with our build options
sed -i -e 's|^CFLAGS_OPT=.*$|CFLAGS_OPT=%{optflags}|' Makefile
sed -i -e 's|^PREFIX=.*$|PREFIX=%{_prefix}|' Makefile
sed -i -e 's|^LIBDIR_NAME=.*$|LIBDIR_NAME=%{_lib}|' Makefile
sed -i -e 's|^SHAREDLIB_DIR=.*$|SHAREDLIB_DIR=%{_libdir}|' Makefile
sed -i -e '/^CFLAGS_OPT=/i LDFLAGS=%{ldflags}' Makefile

%make CC=%{__cc} CXX=%{__cxx}

# build mozilla plugin
%make plugin CC=%{__cc} CXX=%{__cxx}

%install
%makeinstall_std
%ifarch x86_64 aarch64
sed -i 's|${prefix}/lib|${prefix}/lib64|g' %{buildroot}/%{_libdir}/pkgconfig/openh264.pc
%endif

#--------------------------------------------|
#Install mozilla plugin
install -dm 755 %{buildroot}%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed
ln -s %{_bindir}/h264enc %{buildroot}%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed/h264enc
cp -a libgmpopenh264.so* gmpopenh264.info %{buildroot}%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed/

# cofiguration for mozilla plugin
install -dm 755 %{buildroot}%{_libdir}/firefox/defaults/pref
cat > %{buildroot}%{_libdir}/firefox/defaults/pref/gmpopenh264.js << EOF
pref("media.gmp-gmpopenh264.autoupdate", false);
pref("media.gmp-gmpopenh264.version", "system-installed");
pref("media.gmp-gmpopenh264.enabled", true);
pref("media.gmp-gmpopenh264.provider.enabled", true);
pref("media.peerconnection.video.h264_enabled", true);
EOF

install -dm 755 %{buildroot}%{_sysconfdir}/profile.d
cat > %{buildroot}%{_sysconfdir}/profile.d/gmpopenh264.sh << EOF
MOZ_GMP_PATH="%{_libdir}/mozilla/plugins/gmp-gmpopenh264/system-installed"
export MOZ_GMP_PATH
EOF
#end install mozilla plugin
#--------------------------------------------|

# Tools for openh264
install -dm 755 %{buildroot}%{_bindir}
cp -a h264enc h264dec %{buildroot}%{_bindir}/

# Remove static libraries
rm %{buildroot}%{_libdir}/*.a

%files
%{_bindir}/h264enc
%{_bindir}/h264dec

%files -n %{libname}
%{_libdir}/lib%{name}.so.*

%files -n %{devname}
%doc README.md LICENSE CONTRIBUTORS
%{_includedir}/wels
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/*.pc

%files -n mozilla-openh264
%{_sysconfdir}/profile.d/gmpopenh264.sh
%dir %{_libdir}/firefox
%dir %{_libdir}/firefox/defaults
%dir %{_libdir}/firefox/defaults/pref
%{_libdir}/firefox/defaults/pref/gmpopenh264.js
%{_libdir}/mozilla/plugins/gmp-gmpopenh264/
