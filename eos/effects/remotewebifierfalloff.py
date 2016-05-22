# remoteWebifierFalloff
#
# Used by:
# Drones from group: Stasis Webifying Drone (3 of 3)
# Modules from group: Stasis Grappler (7 of 7)
# Modules from group: Stasis Web (18 of 18)
type = "active", "projected"
def handler(fit, module, context):
    if "projected" not in context: return
    fit.ship.boostItemAttr("maxVelocity", module.getModifiedItemAttr("speedFactor"),
                           stackingPenalties = True, remoteResists=True)
