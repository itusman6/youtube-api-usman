from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import yt_dlp
import uvicorn
from typing import List, Optional
import tempfile
import os

app = FastAPI(title="YouTube Downloader API")

# Sample Netscape format cookies (you should replace with your actual cookies)
DEFAULT_COOKIES = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	TRUE	1763511237	GPS	1
.youtube.com	TRUE	/	TRUE	1798069469	PREF	tz=Asia.Karachi
.youtube.com	TRUE	/	TRUE	1779061436	__Secure-YNID	13.YT=pkZxz94iSUNr54AmX3zo-98cD5hP88pQvz1Tq407Z8NK7gj4dd3Y6C9kuOJf0Iu0_HfHpz1XNrcac8V5sP5kx9MzYFig7eiHyjdfXW659at6bf2QREFAHlUkzyU7_aW5jKMn5rK4pF-zUxY0BZtQOpXuw3gBjrk7-TF0W72sxcHHZrCfgBJU3-j1wCrTiX4kfRS6Dt19iJVnuMr8tInzGZA4Wg98haNnXSG6OMazZ7Z666G6rlMgKI_Fzk5VL1VHdG0_pYonHPF5SMz5XWoNx2BxsE8sNKxyQqSbz8Y9mZTIo4pxmkkVib3t5GVi6_OziWNA-spS8CXpu1-6b7kvuw
accounts.google.com	FALSE	/	TRUE	1766101445	OTZ	8353424_36_36__36_
.google.com	TRUE	/	TRUE	1779320645	NID	526=Bz4icB015K_MZMeGmiKwASsNkbRRMduaQNsalt6maDFb4_ni7lcRaLOcnDiha1YKSDQQZ-lO7r2okn2ZKy0FcyzT0UPLbzUbfK5d6B9Bfm6IrsYOy_LrvtEzjBOnpg7SQ93iKiyiO6tdSLJT9wrCo83s1SdmgIaAtCkNTsT0UxcWv76zzigOArVTwUuMBxjSHKRr-6IkqcaFv41D9zRaT4iWwtYc5sB1VdVT8--Rba3gUo6rPnGVFEvAfkO3Z4Ma9hswGPQY4hUy9FDAr-k-7f3MyOLN-sC2i6r8QNwM1k7VxRVs74wAL6rFvNfWLztHxIg12cls7B58b-vYR8Dc8qXbaPs_YJ_DZ9ccn-GVTpiwPCnRbPn8zgYkOKQP2WqUFw6DWH-AcWL5H0lW9CByQaWupc3L8nX8mV0nwwDVqZXLVaAEb0h301KjBvlZ1hw0Pg91gn9Eeb6_CN7UXbGm6cg3-LCZyXFTcxxE6KDquSfBxeCiKKCn-gdy9hMaxgEIAI4aXA4q95Ni3pQXDUC7-NG3Z-dUwEUMB8IuDcsIFbjTmmV9uReJq-M0j5NJ4EKg5I6R70sXnwX2iyCoGI6IgFwc3B8vkqJxUNpo1SeEdCL7K3rNRCvK8LiN9KH6akS9c3F5NnRQDO4l_HU8
.google.com	TRUE	/	FALSE	1798069464	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.google.com	TRUE	/	TRUE	1798069464	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.google.com	TRUE	/	TRUE	1798069464	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.google.com	TRUE	/	FALSE	1798069464	HSID	ALttl9-GAxYV70nOK
.google.com	TRUE	/	TRUE	1798069464	SSID	AWbFNyngz40EOJXSi
.google.com	TRUE	/	FALSE	1798069464	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.google.com	TRUE	/	TRUE	1798069464	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com	TRUE	/	TRUE	1798069464	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com	TRUE	/	TRUE	1798069464	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-GAPS	1:-QodBvu_dLfLHZ-2bUWvRR_MiUWJgEM18bQNQDbGhkxwypuvk1t-vUFVdbcKQv_50NQ5x4eSo-WBAHaUU8vDVt7kg2kCzw:meYOfiKHJ1fWvFhi
accounts.google.com	FALSE	/	TRUE	1798069464	LSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBnXMq-k2kU85-JJNUr1UkwQACgYKAXoSARISFQHGX2MiDts1vSA3PdzjIqAIFylYyBoVAUF8yKqw7IcpWC6Q77WRUSQp2GPh0076
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-1PLSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBuQuilEH0J6ItBnamFqOBwQACgYKASsSARISFQHGX2MibXmtRN0_XW750SeDBpHdBhoVAUF8yKrtC28P3HDwCFk214JeiCo_0076
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-3PLSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBSXaJqJ0vmQpwbSWNITCSdQACgYKAZoSARISFQHGX2MiH2hambezCQudYYxHa-Sc6hoVAUF8yKoaMlYdQBvLa71TXR4y6yND0076
accounts.google.com	FALSE	/	TRUE	1798069464	ACCOUNT_CHOOSER	AFx_qI6AI9JyZjxbUKF6xiBDDJdcNvOuZdF4YuN7TaqiMO2xOAExvfLyW_mXFPXQjoM4zXewLMuKovxChDEdU635fvRfMqQHu3NDD1FFYDMRQOEQYH69u8rJ8aGL2AgOm4T0kfxI1N85
.youtube.com	TRUE	/	TRUE	1795045465	__Secure-1PSIDTS	sidts-CjUBwQ9iI3K2W_UW1y0QT8PYd_OhSjB1n1LQ4B_ojajyUO0a5FGwNHRdYhWZNoS0itaHTdpNRBAA
.youtube.com	TRUE	/	TRUE	1795045465	__Secure-3PSIDTS	sidts-CjUBwQ9iI3K2W_UW1y0QT8PYd_OhSjB1n1LQ4B_ojajyUO0a5FGwNHRdYhWZNoS0itaHTdpNRBAA
.youtube.com	TRUE	/	FALSE	1798069465	HSID	A3ZQtsAe0nIbByNgn
.youtube.com	TRUE	/	TRUE	1798069465	SSID	AT_UW_ygXotrN-yCf
.youtube.com	TRUE	/	FALSE	1798069465	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.youtube.com	TRUE	/	TRUE	1798069465	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	FALSE	1798069465	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.google.com.pk	TRUE	/	FALSE	1798069466	HSID	A3ZQtsAe0nIbByNgn
.google.com.pk	TRUE	/	TRUE	1798069466	SSID	AT_UW_ygXotrN-yCf
.google.com.pk	TRUE	/	FALSE	1798069466	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.google.com.pk	TRUE	/	TRUE	1798069466	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1779320666	NID	526=JWzy9N3DNAleeDifZ4JV1BBqWPmt056vfIT0_d3FXsgaPBQKxVE3iWK4LmuSlGXSbmwIIBpNi1k3k-2A9U29aFqs7n5usOwb1QNdmYmxM4GBvUrAiNIf4S5Y3CgxEmCbT9G1PK2bNYvXhf2ERkjsHEJ7zYrJsBUUkOV8x_LMJ6rngBnrm61ktbSa8BkkfjD_R-EcBWwkFlLKZK8
.google.com.pk	TRUE	/	FALSE	1798069466	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.youtube.com	TRUE	/	TRUE	1798069466	LOGIN_INFO	AFmmF2swRAIgPVCxldJ5__mwMNJnphfb274Y2mlUr4QBrji2NbUZVbYCIDy5FtUqZzVjt4u_Yi8nALGuIyzsCAooIep3Vz49XDLa:QUQ3MjNmeFNqWGw1WWptT01xSjFPQkVhUkhLanpWajlaMEJLcU4xbnNRY21PSnFCOEZ5WElsY1h2X095WXZ6UVAxWWVJMG5RejN2aXhtcUd3TXQtNWNMaTZZS0ZvSUlyWFE4WEVKc2xrOHJ6QVpKRGI3bHNmUEVoc3B6TzhUalZpR196czY3UjFmRmxWblMyc21qajhhXzVKQkwzaTdpUW53
.google.com	TRUE	/	FALSE	1795045466	SIDCC	AKEyXzV9udFuVf9tXyd3xwOlo9GHb6zdHGfSaMlYKV0GBaGW6xIWlbDY-SQlxXAn3tguvO2V
.google.com	TRUE	/	TRUE	1795045466	__Secure-1PSIDCC	AKEyXzUKDHL-pZcLwwCJdgYxTFYWJJYXvPDea2XafA_H2FNgTgt6pmJ2wsffIvXOS2OSObA4
.google.com	TRUE	/	TRUE	1795045466	__Secure-3PSIDCC	AKEyXzUGc0CJ2mY7EUVsIQkiytbmBugRpdR-MpZW2nezk87jf9Z5eu-pYRyL8POYiMkwum0a
.youtube.com	TRUE	/	FALSE	1795045581	SIDCC	AKEyXzVulw6uCBgRUnRjO2a9mCGP9aVTZDCjLLaj6KrN-1NqJ3d0J5N5Mi_RUOraOCHAD0fyRA
.youtube.com	TRUE	/	TRUE	1795045581	__Secure-1PSIDCC	AKEyXzVKmky4ROMQGgG_JG_8FIbd84t3LaiWwiLtA0qaHHL1c6ZPZqX7E9YLGxSyGH_5WSA6
.youtube.com	TRUE	/	TRUE	1795045581	__Secure-3PSIDCC	AKEyXzUwrA0-WSIVwF7CP1HeeSOYKWrYx4lqigSqJx0qKTwHOIO8lz27YwvEwA0QnElCJprfaA
.youtube.com	TRUE	/	TRUE	1763511237	GPS	1
.youtube.com	TRUE	/	TRUE	0	YSC	CzbXFJf6Nqw
.youtube.com	TRUE	/	TRUE	1779061472	VISITOR_INFO1_LIVE	WdQFwChI768
.youtube.com	TRUE	/	TRUE	1779061472	VISITOR_PRIVACY_METADATA	CgJQSxIEGgAgJA%3D%3D
.youtube.com	TRUE	/	TRUE	1798069469	PREF	tz=Asia.Karachi
.youtube.com	TRUE	/	TRUE	1779061436	__Secure-YNID	13.YT=pkZxz94iSUNr54AmX3zo-98cD5hP88pQvz1Tq407Z8NK7gj4dd3Y6C9kuOJf0Iu0_HfHpz1XNrcac8V5sP5kx9MzYFig7eiHyjdfXW659at6bf2QREFAHlUkzyU7_aW5jKMn5rK4pF-zUxY0BZtQOpXuw3gBjrk7-TF0W72sxcHHZrCfgBJU3-j1wCrTiX4kfRS6Dt19iJVnuMr8tInzGZA4Wg98haNnXSG6OMazZ7Z666G6rlMgKI_Fzk5VL1VHdG0_pYonHPF5SMz5XWoNx2BxsE8sNKxyQqSbz8Y9mZTIo4pxmkkVib3t5GVi6_OziWNA-spS8CXpu1-6b7kvuw
.youtube.com	TRUE	/	TRUE	1779061438	__Secure-ROLLOUT_TOKEN	CKGemaKMwPeN4QEQk8rPy_D8kAMYmujBzPD8kAM%3D
.youtube.com	TRUE	/	TRUE	1779061437	__Secure-YNID	13.YT=Ud-NmKt6CJJgol0WW2DkWDe3Am7g793A0Rpbg-OfeT05GJSitNwX2QL9ocvhwyVpLH6L9Kj1AAI09tp4Qtz3V8ZnLjIc6eDDImjhdgA8WJNygAExO3attChhT62RgBhi0NZqjoeKZlwW3PpRFtcUPrMnUKrQlUzRevWMgkvdnllJolEYTlzP9EO6qJFPeqiW9X66RupwQpHn924UyRgAP5ugBCufJ7yUYnL8wwqHjCoAlNKAw81huwgjJMpsQ9eI1o1oRktBSUyZh6Q8NuzP1hx2zpPXZUKHg2k91XUeaQDRS4YE07WT6Jv4gWGJW2kWDrhQ3W-Rrh0o66k1OOgqNw
accounts.google.com	FALSE	/	TRUE	1766101445	OTZ	8353424_36_36__36_
.google.com	TRUE	/	TRUE	1779320645	NID	526=Bz4icB015K_MZMeGmiKwASsNkbRRMduaQNsalt6maDFb4_ni7lcRaLOcnDiha1YKSDQQZ-lO7r2okn2ZKy0FcyzT0UPLbzUbfK5d6B9Bfm6IrsYOy_LrvtEzjBOnpg7SQ93iKiyiO6tdSLJT9wrCo83s1SdmgIaAtCkNTsT0UxcWv76zzigOArVTwUuMBxjSHKRr-6IkqcaFv41D9zRaT4iWwtYc5sB1VdVT8--Rba3gUo6rPnGVFEvAfkO3Z4Ma9hswGPQY4hUy9FDAr-k-7f3MyOLN-sC2i6r8QNwM1k7VxRVs74wAL6rFvNfWLztHxIg12cls7B58b-vYR8Dc8qXbaPs_YJ_DZ9ccn-GVTpiwPCnRbPn8zgYkOKQP2WqUFw6DWH-AcWL5H0lW9CByQaWupc3L8nX8mV0nwwDVqZXLVaAEb0h301KjBvlZ1hw0Pg91gn9Eeb6_CN7UXbGm6cg3-LCZyXFTcxxE6KDquSfBxeCiKKCn-gdy9hMaxgEIAI4aXA4q95Ni3pQXDUC7-NG3Z-dUwEUMB8IuDcsIFbjTmmV9uReJq-M0j5NJ4EKg5I6R70sXnwX2iyCoGI6IgFwc3B8vkqJxUNpo1SeEdCL7K3rNRCvK8LiN9KH6akS9c3F5NnRQDO4l_HU8
.google.com	TRUE	/	FALSE	1798069464	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.google.com	TRUE	/	TRUE	1798069464	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.google.com	TRUE	/	TRUE	1798069464	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.google.com	TRUE	/	FALSE	1798069464	HSID	ALttl9-GAxYV70nOK
.google.com	TRUE	/	TRUE	1798069464	SSID	AWbFNyngz40EOJXSi
.google.com	TRUE	/	FALSE	1798069464	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.google.com	TRUE	/	TRUE	1798069464	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com	TRUE	/	TRUE	1798069464	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com	TRUE	/	TRUE	1798069464	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-GAPS	1:-QodBvu_dLfLHZ-2bUWvRR_MiUWJgEM18bQNQDbGhkxwypuvk1t-vUFVdbcKQv_50NQ5x4eSo-WBAHaUU8vDVt7kg2kCzw:meYOfiKHJ1fWvFhi
accounts.google.com	FALSE	/	TRUE	1798069464	LSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBnXMq-k2kU85-JJNUr1UkwQACgYKAXoSARISFQHGX2MiDts1vSA3PdzjIqAIFylYyBoVAUF8yKqw7IcpWC6Q77WRUSQp2GPh0076
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-1PLSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBuQuilEH0J6ItBnamFqOBwQACgYKASsSARISFQHGX2MibXmtRN0_XW750SeDBpHdBhoVAUF8yKrtC28P3HDwCFk214JeiCo_0076
accounts.google.com	FALSE	/	TRUE	1798069464	__Host-3PLSID	s.PK|s.youtube:g.a0003wgENmQcNev-BoB2F5yDkjiKBBC3gEefOP9cpS7LZosEgVvBSXaJqJ0vmQpwbSWNITCSdQACgYKAZoSARISFQHGX2MiH2hambezCQudYYxHa-Sc6hoVAUF8yKoaMlYdQBvLa71TXR4y6yND0076
accounts.google.com	FALSE	/	TRUE	1798069464	ACCOUNT_CHOOSER	AFx_qI6AI9JyZjxbUKF6xiBDDJdcNvOuZdF4YuN7TaqiMO2xOAExvfLyW_mXFPXQjoM4zXewLMuKovxChDEdU635fvRfMqQHu3NDD1FFYDMRQOEQYH69u8rJ8aGL2AgOm4T0kfxI1N85
.youtube.com	TRUE	/	TRUE	1795045465	__Secure-1PSIDTS	sidts-CjUBwQ9iI3K2W_UW1y0QT8PYd_OhSjB1n1LQ4B_ojajyUO0a5FGwNHRdYhWZNoS0itaHTdpNRBAA
.youtube.com	TRUE	/	TRUE	1795045465	__Secure-3PSIDTS	sidts-CjUBwQ9iI3K2W_UW1y0QT8PYd_OhSjB1n1LQ4B_ojajyUO0a5FGwNHRdYhWZNoS0itaHTdpNRBAA
.youtube.com	TRUE	/	FALSE	1798069465	HSID	A3ZQtsAe0nIbByNgn
.youtube.com	TRUE	/	TRUE	1798069465	SSID	AT_UW_ygXotrN-yCf
.youtube.com	TRUE	/	FALSE	1798069465	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.youtube.com	TRUE	/	TRUE	1798069465	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.youtube.com	TRUE	/	FALSE	1798069465	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.youtube.com	TRUE	/	TRUE	1798069465	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.google.com.pk	TRUE	/	FALSE	1798069466	HSID	A3ZQtsAe0nIbByNgn
.google.com.pk	TRUE	/	TRUE	1798069466	SSID	AT_UW_ygXotrN-yCf
.google.com.pk	TRUE	/	FALSE	1798069466	APISID	z_0Rh5AEzBXP3OHM/AfTZwOfB0HChzdmY1
.google.com.pk	TRUE	/	TRUE	1798069466	SAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-1PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-3PAPISID	fj-F6CtSaEtHo8VU/ACT04OtbhnXjPC1lk
.google.com.pk	TRUE	/	TRUE	1779320666	NID	526=JWzy9N3DNAleeDifZ4JV1BBqWPmt056vfIT0_d3FXsgaPBQKxVE3iWK4LmuSlGXSbmwIIBpNi1k3k-2A9U29aFqs7n5usOwb1QNdmYmxM4GBvUrAiNIf4S5Y3CgxEmCbT9G1PK2bNYvXhf2ERkjsHEJ7zYrJsBUUkOV8x_LMJ6rngBnrm61ktbSa8BkkfjD_R-EcBWwkFlLKZK8
.google.com.pk	TRUE	/	FALSE	1798069466	SID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_TDXqBPcPZXlMBi0CsfN2GwACgYKAScSARISFQHGX2MihBcp0ThhhvjhCGytg25xJBoVAUF8yKpclZp3a68J-bTLzgeZuLyx0076
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-1PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_KYVkmClMD6mIjFh4QksEIQACgYKAd4SARISFQHGX2Mi-ZYknvSAU6O_zLRLj2r-ERoVAUF8yKoyNys4e9qU6xgBv-FcLnNt0076
.google.com.pk	TRUE	/	TRUE	1798069466	__Secure-3PSID	g.a0003wgENuqTpade-q6Ggz580tb0lH7iXEBZcW_hwG3jNLcR09q_wSLG27i6nnMekRJ4y6-8nwACgYKAUASARISFQHGX2MiSyjClZnPWndGqIKRyHVIqhoVAUF8yKqoabEzEVDySGIpCksTtXbo0076
.youtube.com	TRUE	/	TRUE	1798069466	LOGIN_INFO	AFmmF2swRAIgPVCxldJ5__mwMNJnphfb274Y2mlUr4QBrji2NbUZVbYCIDy5FtUqZzVjt4u_Yi8nALGuIyzsCAooIep3Vz49XDLa:QUQ3MjNmeFNqWGw1WWptT01xSjFPQkVhUkhLanpWajlaMEJLcU4xbnNRY21PSnFCOEZ5WElsY1h2X095WXZ6UVAxWWVJMG5RejN2aXhtcUd3TXQtNWNMaTZZS0ZvSUlyWFE4WEVKc2xrOHJ6QVpKRGI3bHNmUEVoc3B6TzhUalZpR196czY3UjFmRmxWblMyc21qajhhXzVKQkwzaTdpUW53
.google.com	TRUE	/	FALSE	1795045466	SIDCC	AKEyXzV9udFuVf9tXyd3xwOlo9GHb6zdHGfSaMlYKV0GBaGW6xIWlbDY-SQlxXAn3tguvO2V
.google.com	TRUE	/	TRUE	1795045466	__Secure-1PSIDCC	AKEyXzUKDHL-pZcLwwCJdgYxTFYWJJYXvPDea2XafA_H2FNgTgt6pmJ2wsffIvXOS2OSObA4
.google.com	TRUE	/	TRUE	1795045466	__Secure-3PSIDCC	AKEyXzUGc0CJ2mY7EUVsIQkiytbmBugRpdR-MpZW2nezk87jf9Z5eu-pYRyL8POYiMkwum0a
.youtube.com	TRUE	/	FALSE	1795045581	SIDCC	AKEyXzVulw6uCBgRUnRjO2a9mCGP9aVTZDCjLLaj6KrN-1NqJ3d0J5N5Mi_RUOraOCHAD0fyRA
.youtube.com	TRUE	/	TRUE	1795045581	__Secure-1PSIDCC	AKEyXzVKmky4ROMQGgG_JG_8FIbd84t3LaiWwiLtA0qaHHL1c6ZPZqX7E9YLGxSyGH_5WSA6
.youtube.com	TRUE	/	TRUE	1795045581	__Secure-3PSIDCC	AKEyXzUwrA0-WSIVwF7CP1HeeSOYKWrYx4lqigSqJx0qKTwHOIO8lz27YwvEwA0QnElCJprfaA
"""

def get_cookies_file():
    """Create temporary cookies file from DEFAULT_COOKIES"""
    if DEFAULT_COOKIES.strip():
        try:
            temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt')
            temp_file.write(DEFAULT_COOKIES)
            temp_file.close()
            return temp_file.name
        except Exception as e:
            print(f"Error creating cookies file: {e}")
    return None

def extract_info(url: str):
    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
    }
    
    # Add cookies if available
    cookies_path = get_cookies_file()
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
        print("Using cookies for extraction")

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Clean up cookies file
        if cookies_path and os.path.exists(cookies_path):
            os.unlink(cookies_path)
            
        return info


@app.get("/api/info")
def get_info(url: str = Query(...)):
    try:
        info = extract_info(url)

        formats = []

        for f in info.get("formats", []):
            formats.append({
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "filesize": f.get("filesize"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio": f.get("acodec") != "none",
                "video": f.get("vcodec") != "none",
                "audio_codec": f.get("acodec"),
                "video_codec": f.get("vcodec"),
                "fps": f.get("fps"),
                "audio_bitrate": f.get("abr"),
                "url": f.get("url"),
                "format_note": f.get("format_note", ""),
                "quality": f.get("quality"),
            })

        return {
            "status": True,
            "id": info.get("id"),
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "duration_string": info.get("duration_string"),
            "uploader": info.get("uploader"),
            "view_count": info.get("view_count"),
            "like_count": info.get("like_count"),
            "categories": info.get("categories", []),
            "tags": info.get("tags", []),
            "description": info.get("description"),
            "formats": formats,
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/mp3")
def get_mp3(url: str = Query(...), quality: Optional[str] = Query("best")):
    try:
        info = extract_info(url)
        audio_formats = [
            f for f in info["formats"] 
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        if quality == "best":
            best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0, reverse=True)[0]
        elif quality == "worst":
            best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0)[0]
        else:
            # Try to find specific quality
            quality_audio = [f for f in audio_formats if f.get("format_note", "").lower() == quality.lower()]
            if quality_audio:
                best_audio = quality_audio[0]
            else:
                best_audio = sorted(audio_formats, key=lambda x: x.get("abr", 0) or 0, reverse=True)[0]

        return {
            "status": True,
            "format": "audio",
            "ext": best_audio["ext"],
            "bitrate": best_audio.get("abr"),
            "filesize_mb": round(best_audio.get("filesize", 0) / (1024 * 1024), 2) if best_audio.get("filesize") else None,
            "audio_codec": best_audio.get("acodec"),
            "url": best_audio["url"],
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/mp4")
def get_mp4(url: str = Query(...), quality: Optional[str] = Query("best")):
    try:
        info = extract_info(url)
        video_formats = [
            f for f in info["formats"] 
            if f.get("vcodec") != "none" and f.get("acodec") != "none"
        ]

        if quality == "best":
            best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0), reverse=True)[0]
        elif quality == "worst":
            best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0))[0]
        else:
            # Try to find specific resolution
            quality_videos = [f for f in video_formats if f.get("format_note", "").lower() == quality.lower()]
            if quality_videos:
                best_video = quality_videos[0]
            else:
                best_video = sorted(video_formats, key=lambda x: (x.get("height") or 0, x.get("fps") or 0), reverse=True)[0]

        return {
            "status": True,
            "format": "video",
            "resolution": best_video.get("resolution"),
            "height": best_video.get("height"),
            "ext": best_video["ext"],
            "filesize_mb": round(best_video.get("filesize", 0) / (1024 * 1024), 2) if best_video.get("filesize") else None,
            "fps": best_video.get("fps"),
            "audio_codec": best_video.get("acodec"),
            "video_codec": best_video.get("vcodec"),
            "url": best_video["url"],
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/all-formats")
def get_all_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        
        # Categorize formats
        audio_only = []
        video_only = []
        video_audio = []
        
        for f in info.get("formats", []):
            format_info = {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio_codec": f.get("acodec"),
                "video_codec": f.get("vcodec"),
                "fps": f.get("fps"),
                "audio_bitrate": f.get("abr"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            
            has_audio = f.get("acodec") != "none"
            has_video = f.get("vcodec") != "none"
            
            if has_audio and not has_video:
                audio_only.append(format_info)
            elif has_video and not has_audio:
                video_only.append(format_info)
            elif has_video and has_audio:
                video_audio.append(format_info)

        return {
            "status": True,
            "title": info.get("title"),
            "audio_only_formats": sorted(audio_only, key=lambda x: x.get("audio_bitrate", 0) or 0, reverse=True),
            "video_only_formats": sorted(video_only, key=lambda x: x.get("height", 0) or 0, reverse=True),
            "video_audio_formats": sorted(video_audio, key=lambda x: x.get("height", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/download")
def download_format(url: str = Query(...), format_id: str = Query(...)):
    try:
        info = extract_info(url)
        
        # Find the specific format
        selected_format = None
        for f in info.get("formats", []):
            if f.get("format_id") == format_id:
                selected_format = f
                break
        
        if not selected_format:
            return JSONResponse({"status": False, "error": "Format not found"}, status_code=404)

        return {
            "status": True,
            "title": info.get("title"),
            "format_id": selected_format.get("format_id"),
            "ext": selected_format.get("ext"),
            "resolution": selected_format.get("resolution"),
            "filesize_mb": round(selected_format.get("filesize", 0) / (1024 * 1024), 2) if selected_format.get("filesize") else None,
            "audio_codec": selected_format.get("acodec"),
            "video_codec": selected_format.get("vcodec"),
            "url": selected_format.get("url"),
            "direct_download_url": selected_format.get("url"),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/audio-formats")
def get_audio_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        audio_formats = [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "bitrate": f.get("abr"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "audio_codec": f.get("acodec"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            for f in info["formats"] 
            if f.get("acodec") != "none" and f.get("vcodec") == "none"
        ]

        return {
            "status": True,
            "title": info.get("title"),
            "audio_formats": sorted(audio_formats, key=lambda x: x.get("bitrate", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


@app.get("/api/video-formats")
def get_video_formats(url: str = Query(...)):
    try:
        info = extract_info(url)
        video_formats = [
            {
                "format_id": f.get("format_id"),
                "ext": f.get("ext"),
                "resolution": f.get("resolution") or f"{f.get('height', 'N/A')}p",
                "height": f.get("height"),
                "filesize_mb": round(f.get("filesize", 0) / (1024 * 1024), 2) if f.get("filesize") else None,
                "fps": f.get("fps"),
                "video_codec": f.get("vcodec"),
                "audio_codec": f.get("acodec"),
                "format_note": f.get("format_note", ""),
                "url": f.get("url"),
            }
            for f in info["formats"] 
            if f.get("vcodec") != "none"
        ]

        return {
            "status": True,
            "title": info.get("title"),
            "video_formats": sorted(video_formats, key=lambda x: x.get("height", 0) or 0, reverse=True),
        }

    except Exception as e:
        return JSONResponse({"status": False, "error": str(e)}, status_code=500)


# --------------------------------------------------------
# 🚀 Run server via: python main.py
# --------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )





