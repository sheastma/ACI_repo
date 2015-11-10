from bottle import route, run, template
import elam_aci

@route('/index.html')
def index():
    f = open('elam_test.html')
    return f.read()


@route('/elam/<data>', method = "GET")
def elam(data):
    spl = data.split(',')
    response = elam_aci.main(spl[0],spl[1],spl[2],spl[3],spl[4],spl[5])
    return response

run(host='localhost', port=8082)
