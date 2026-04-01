package main

import (
	"fmt"
	"net"
	"net/http"
	"os"
)

var version = "dev"

func handler(w http.ResponseWriter, r *http.Request) {
	hostname, _ := os.Hostname()

	addrs, err := net.LookupIP(hostname)
	if err != nil {
		fmt.Fprintf(w, "Failed to detect IP: %v\n", err)
		return
	}

	ip := "unknown"
	for _, addr := range addrs {
		if ipv4 := addr.To4(); ipv4 != nil {
			ip = ipv4.String()
			break
		}
	}

	fmt.Fprintf(w, "IP: %s\nHostname: %s\nVersion: %s\n", ip, hostname, version)
}

func main() {
	http.HandleFunc("/", handler)
	http.ListenAndServe(":8080", nil)
}
