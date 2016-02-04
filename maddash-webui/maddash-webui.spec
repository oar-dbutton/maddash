%define package_name maddash-webui 
%define install_base /usr/lib/maddash/%{package_name}
%define config_base /etc/maddash/%{package_name}
%define relnum 0.0.a1

Name:           %{package_name}
Version:        1.3
Release:        %{relnum}
Summary:        MaDDash Web Interface 
License:        distributable, see LICENSE
Group:          Development/Libraries
URL:            http://code.google.com/p/esnet-perfsonar
Source0:        maddash-%{version}-%{relnum}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       perl
Requires:       httpd 
Requires:       mod_ssl

%description
MaDDash is a framework for scheduling service checks and displaying results in a grid. 
This package provides a web interface to display check results.

%pre
/usr/sbin/groupadd maddash 2> /dev/null || :
/usr/sbin/useradd -g maddash -r -s /sbin/nologin -c "MaDDash User" -d /tmp maddash 2> /dev/null || :

%prep
%setup -q -n maddash-%{version}-%{relnum}

%clean
rm -rf %{buildroot}

%build
%{package_name}/scripts/build_dojo.sh %{package_name}/dojo-build

%install
#Clean out previous build
rm -rf %{buildroot}

#Create directory structure for build root
mkdir -p %{buildroot}/%{install_base}
mkdir -p %{buildroot}/%{config_base}
mkdir -p %{buildroot}/etc/httpd/conf.d

#Copy jar files and scripts
install -m 755 %{package_name}/web/*.cgi %{buildroot}/%{install_base}/
install -m 644 %{package_name}/etc/apache-maddash.conf  %{buildroot}/etc/httpd/conf.d/
install -m 644 %{package_name}/web/etc/* %{buildroot}/%{config_base}/
cp -r %{package_name}/web/admin %{buildroot}/%{install_base}/admin
cp -r %{package_name}/web/lib %{buildroot}/%{install_base}/lib
cp -r %{package_name}/web/style %{buildroot}/%{install_base}/style
cp -r %{package_name}/web/images %{buildroot}/%{install_base}/images

%post
#create empty directory for config files. apache user files can go here
mkdir -p /etc/maddash/maddash-webui
touch /etc/maddash/maddash-webui/admin-users
chown apache:apache /etc/maddash/maddash-webui/admin-users
chmod 600 /etc/maddash/maddash-webui/admin-users

if [ "$1" = "2" ]; then
    #Replace pre-1.3 file
    if [ -e %{install_base}/etc/config.json ] && [ ! -L %{install_base}/etc/config.json ]; then
        mv %{config_base}/etc/config.json %{config_base}/etc/config.json.bak
        mv %{install_base}/etc/config.json %{config_base}/etc/config.json
    fi
    
    #update apache config
    sed -i "s:/opt/maddash:/usr/lib/maddash:g" /etc/httpd/conf.d/apache-maddash.conf
fi

#create symlink to config.json
if [ ! -e %{install_base}/etc/config.json ]; then
    ln -s %{config_base}/etc/config.json %{install_base}/etc/config.json
fi

#restart apache so config changes are applied
/etc/init.d/httpd restart

%files
%defattr(-,maddash,maddash,-)
%config(noreplace) /etc/httpd/conf.d/apache-maddash.conf
%config(noreplace) %{config_base}/config.json
%{config_base}/config.example.json
%{install_base}/*

%preun

