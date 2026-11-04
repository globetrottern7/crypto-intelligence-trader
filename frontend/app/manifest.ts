import type { MetadataRoute } from "next";
export default function manifest(): MetadataRoute.Manifest {
  return { name:"Crypto Intelligence & Trading Assistant", short_name:"Crypto Intel", description:"Personal digital-asset market intelligence and paper-trading workspace.", start_url:"/", display:"standalone", background_color:"#0b1220", theme_color:"#0b1220" };
}
