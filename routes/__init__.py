from routes.users_routes import router as users_routes
from routes.index import router as index
from routes.auth import router as auth
from routes.company_routes import router as company_routes
from routes.roles_routes import router as roles_routes
from routes.school_routes import router as school_routes
from routes.programs_routes import router as programs_routes
from routes.quotes_routes import router as quotes_routes
from routes.sales_routes import router as sales_routes
from routes.pasajeros_routes import router as pasajeros_routes
from routes.voucher_routes import router as voucher_routes
from routes.opening_routes import router as opening_routes
from routes.pay_routes import router as pay_routes
from routes.trbnkpagos_routes import router as trbnkpagos_routes
from routes.flowpagos_routes import router as flowpagos_routes
from routes.mercadopago_routes import router as mercadopago_routes
from routes.payment_routes import router as payment_routes
from routes.gateways_routes import router as gateways_routes
from routes.entry_routes import router as entry_routes
from routes.gdsair_routes import router as gdsair_routes
from routes.gdshotel_routes import router as gdshotel_routes

# Lista de routers centralizada
all_routers = [
    (users_routes, "/users"),        # (router, prefix)
    (index, ""),                     # index no tiene prefijo
    (auth, ""),                      # auth no tiene prefijo
    (company_routes, "/company"),
    (roles_routes, "/roles"),
    (school_routes, "/schools"),
    (programs_routes, "/programs"),
    (quotes_routes, "/quotes"),
    (sales_routes, "/sales"),
    (pasajeros_routes, "/pasajeros"),
    (voucher_routes, "/voucher"),
    (opening_routes, "/opening"),
    (pay_routes, "/pay"),
    (trbnkpagos_routes, "/trbnkpagos"),
    (flowpagos_routes, "/flowpagos"),
    (mercadopago_routes, "/mercadopago"),
    (payment_routes, "/payment"),
    (gateways_routes, "/gateways"),
    (entry_routes, "/entry"),
    (gdsair_routes, "/gdsair"),
    (gdshotel_routes, "/gdshotel")
]