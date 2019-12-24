#!/bin/bash

setup(){
  export RTE_ANS=/s1/dpdk-ans
  DPDK_DIR=$RTE_ANS/dpdk-18.11
  export RTE_SDK=$DPDK_DIR
  export RTE_TARGET=x86_64-native-linuxapp-gcc
  make config T=x86_64-native-linuxapp-gcc
  make install T=x86_64-native-linuxapp-gcc DESTDIR=x86_64-native-linuxapp-gcc
  KMOD_DIR=$DPDK_DIR/x86_64-native-linuxapp-gcc/kmod/
  insmod $KMOD_DIR/igb_uio.ko
  insmod $KMOD_DIR/rte_kni.ko
  TOOLS_DIR=$DPDK_DIR/usertools/
  #python $DPDK_DIR/usertools/dpdk-devbind.py --status
  #ETH=`python $DPDK_DIR/usertools/dpdk-devbind.py --status |grep 10-Gigabit|grep -v Active|awk -F"if=" '{print $2}'|awk '{print $1}'`
  cd $RTE_ANS/ans
  # ans_main.h    #define MAX_TX_BURST 1
  make
  ########### /usr/local/nginx
  cd $RTE_ANS/dpdk-nginx
  ./configure  --with-http_dav_module
  make && make install
}
#ans_svc nginx 1 "0000:06:00.1" 
#ans_svc wrk   2 "0000:06:00.0" 
ans_svc(){
  #--enable-kni --enable-ipsync  --enable-jumbo --max-pkt-len 9001
  #-w = --pci-whitelist
  #-l = --lcore
  #-n #memory channels
  #--
  #-p #port mask
  #--config=(port,queue,lcore)
  MEM="--base-virtaddr=0x2aaa2aa0000"
  PREFIX=$1
  C=$2
  PCI="-w $3"
  CPU="-l $C -n 4 -- -p 0x1 --config='(0,0,$C)'"
  echo "starting $PREFIX"
  ANS="ans/build/ans"
  if [ "$PREFIX" == "nginx" ]; then
    nohup $ANS $PCI $CPU > ans.$PREFIX.log 2>&1 &
  else
    nohup $ANS $PREFIX $PCI $MEM $CPU > ans.$PREFIX.log 2>&1 &
  fi
  sleep 10
}
nginx(){
  IP=$1  #10.0.0.2
  sleep 5
  CMD="/usr/local/nginx/sbin/nginx"
  nohup $CMD > nginx.log 2>&1 &
  sleep 2
}

  echo "starting ans.wrk"
  PREFIX="--file-prefix=wrks"
  PCI="-w 0000:06:00.0 "  #dr1.wrk
  CPU2="-l 2 -n 4 -- -p 0x1 --config='(0,0,2)'"
  MEM="--base-virtaddr=0x2aaa2aa0000"
  nohup $CMD $PREFIX $PCI $MEM $CPU2 > ans.wrk.log 2>&1 &
  echo "starting 10s"
add_ip(){
  IP=$1  #10.0.0.2
  CLI="cli/build/anscli"
  $CLI $PREFIX "ip addr add $IP/24 dev veth0"
  $CLI $PREFIX "ip addr show"
  sleep 1
}

stops(){
  NAME=$1
  echo "stopping $NAME services"
  pkill $NAME
  ps -ef|grep $NAME|awk '{print $2}'
}
stops ans
stops nginx
#svc 10.10.10.2
ans_svc nginx 1 "0000:06:00.1"
ans_svc wrk   2 "0000:06:00.0"
