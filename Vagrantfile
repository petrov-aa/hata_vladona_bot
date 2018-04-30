# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "ubuntu/xenial64"
  config.vm.network "forwarded_port", guest: 80, host: 8080, host_ip: "127.0.0.1"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "512"
    vb.cpus = "1"
  end

  config.vm.synced_folder "./", "/vagrant", id: "vagrant-root",
      owner: "vagrant",
      group: "vagrant",
      mount_options: ["dmode=775,fmode=664"]

end
