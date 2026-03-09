# SRM-reboot
Home Assistant Integration to reboot a Synology router by using an API call.

This integration has been written to solve a problem that a Synology RT2600ac router does not forward ports from Internet anymore. The router itself is accessable but the devices behind it cannot be reached. A reset solves it but it is not clear what the cause is.

So this is a hack. From the internet a call is made to a Home Assistant webhook. When that webhook is contacted, it will reset the missed ingress counter. (action: srm_reboot.reset_ingress_missed)

The user needs to set up an automation that will increase the counter, most likely based on an interval. You can set it for every hour, 15 minutes, whatever you prefer. As long as you do not reach the limit before the webhook is called, otherwise your router will reset every time. (action: srm_reboot.increase_ingress_missed)

When the ingress missed value hits the limit value, the binary sensor srm_reboot_ingress_blocked will become true. You can use that sensor to trigger the automation to reset the router (action: srm_reboot.reboot) so that hopefully the router will handle the port forwarding correctly again. The srm_reboot_ingress_missed counter is NOT resetting automatically. You need to do that yourself by calling action srm_reboot.reset_ingress_missed. Resetting the counter (or assigning a 0 to it) will also turn off the binary sensor.
