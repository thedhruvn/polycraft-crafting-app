import React from 'react'
import { Divider, Card, Spin } from 'antd'
import { Link } from 'react-router-dom'
import moment from 'moment'
import { Base64 } from 'js-base64'
import mermaid from 'mermaid'

class Preview extends React.Component {
  constructor (props) {
    super(props)
    this.onDownloadSVG = this.onDownloadSVG.bind(this)
    this.state = {
        loading: true,
        cur_state: "INIT",
    }
  }

  onDownloadSVG (event) {
    event.target.href = `data:image/svg+xml;base64,${Base64.encode(
      this.container.innerHTML
    )}`
    event.target.download = `mermaid-diagram-${moment().format(
      'YYYYMMDDHHmmss'
    )}.svg`
  }

  render () {
    console.log("Preview Render Called. Current State: " + this.state.cur_state + " Load: " + this.state.loading)
    const {
      code,
      match: { url }
    } = this.props
    var should_spinner = this.state.loading
//    switch (this.state.cur_state) {
//        case "INIT":
//             should_spinner = true;
//             break;
//        case "READY":
//             should_spinner = false;
//             break;
//        case "NEW_CODE":
//            should_spinner = true;
//            break;
//        case "GEN_MERMAID":
//            should_spinner = true;
//
//            break;
//        default:
//            should_spinner = true;
//            break;
//    }
    return (
        <div>
            <Spin spinning={should_spinner}>
            <Card title='Crafting Diagram'>
                  <div id='main_column'
                    ref={div => {
                      this.container = div
                    }}
                  >
                    {code}
                  </div>
                </Card>
            </Spin>
                <Card title='Actions' size='small'>
                  <div className='links'>
                    <Link to={url.replace('/edit/', '/view/')}>Link to View</Link>
                    <Divider type='vertical' />
                    <a href='' download='' onClick={this.onDownloadSVG}>
                      Download SVG
                    </a>
                  </div>
                </Card>
              </div>

    );

  }

  reset_controller = () => {
    console.log("Reset Controller - new code")
    this.getMermaid().then(() => {
        this.setState({loading: false});
    });
//    this.setState({loading: true, cur_state: "NEW_CODE"})
//    this.state = {
//        loading: true,
//        cur_state: "NEW_CODE",
//    } //don't trigger another state change by mutating.
//    this.initMermaid()

  }

  getMermaid = () => {
    var that = this;
    return new Promise((resolve, reject) => {
        const {
            code,
            history,
            match: { url }
        } = that.props
        try {
//            this.setState({cur_state: "GEN_MERMAID", loading: true})
            console.log("Promised Start")
            console.log({"data": code})
            mermaid.parse(`${code}`)
            console.log("Mermaid parsed successfully")
            // Replacing special characters '<' and '>' with encoded '&lt;' and '&gt;'
            let _code = code
            _code = _code.replace(/</g, '&lt;')
            _code = _code.replace(/>/g, '&gt;')
            console.log("printing _code")
            console.log(_code)
            //      return _code
            // Overriding the innerHTML with the updated code string
            that.container.innerHTML = _code
            resolve(mermaid.init(undefined, that.container));
            //      this.setState({loading: false})
            } catch (e) {
            // {str, hash}
            const base64 = Base64.encodeURI(e.str || e.message)
            history.push(`${url}/error/${base64}`)
            reject();
            }
        });
  }

  shouldComponentUpdate(nextProps, nextState) {
    console.log(`Preview shouldCompUpdate method. state:${this.state.cur_state} ${this.state.loading}. Next: ${nextState.cur_state} ${nextState.loading}`)
    if (this.props.code === nextProps.code) {
        console.log("Code hasn't changed - what gives")
        if (this.state.loading ===false && nextState.loading===true){
            console.log("New Code!")
            return true

        } else if (nextState.loading === false && this.state.loading === true){
            //return to normal - remove the spins
            console.log("ResetCode")
            return true
        }
        else{
            return false
        }

//        if (this.state.cur_state === "INIT" && nextState.cur_state === "READY") {
//            //initial case - allow rendering but reset loading to false after
//            console.log("initial case - allow rendering")
//            this.setState({loading: false})
//            return true
//        }
//        //case rendering complete
//        if(this.state.cur_state === "READY" && nextState.loading === false){
//            console.log("Loading Complete")
//            if(this.state.loading === false){
//                return false //end case
//            }
//            return true
//        }
//        //Case: New Code Received
//        if(this.state.cur_state === "READY" && nextState.cur_state === "NEW_CODE"){
//            this.initMermaid() //update mermaid - loading should already be occurring.
//            return true
//        }
//        //case Mermaid Completed
//        if(this.state.cur_state === "NEW_CODE" && nextState.cur_state === "GEN_MERMAID"){
//            //mermaid loading is complete. Remove loading screen
//            this.setState({loading: false})
//            return true
//        }
//        //case Reset Loading Screen back to ready
//        if(this.state.cur_state === "GEN_MERMAID" && nextState.loading === false){
//            console.log("GenMermaid Complete - turn off loading screen")
//            this.setState({cur_state: "READY"})
//            return true
//        }
        //case Mermaid Completed

    //case new code received.
    } else {
        //New Code
        console.log("Code changed - what gives")
//        this.reset_controller()
        this.state.loading = true
//        this.reset_controller()
        return true

    }

  }

  componentDidMount () {
    console.log("Preview componentDidMount method")
//    this.setState({loading: false})
    this.getMermaid().then(() => {
        this.setState({loading: false});
    });
    this.container.removeAttribute('data-processed')
//    this.setState({cur_state: "READY"})
  }

  componentDidUpdate () {
    console.log("Preview componentDidUpdate")
    this.container.removeAttribute('data-processed')
    if (this.state.loading === true) {

        console.log("Do I generate the promise here?")
        setTimeout(null, 25);
        this.getMermaid().then(() => {
        this.props.toggleSpin();
        this.setState({loading: false});
    });
//        this.reset_controller()
    }
//    this.getMermaid().then(() => {
//        this.setState({loading: false});
//    });
//    if (this.state.cur_state === "GEN_MERMAID") {
//        this.setState({loading: false})
//    }
//    this.setState({loading: false})
//    this.container.innerHTML = this.props.code.replace(
//        'onerror=',
//        'onerror&equals;'
//    )
//    this.initMermaid()
//    if (false) {
//        this.handleMermaid()
////        console.log("Do nothing... Awaiting Load")
//    }else{
//        this.handleMermaid()


//        this.handleMermaid()
//    }
  }
}

export default Preview
