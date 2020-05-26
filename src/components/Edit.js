import React, { useState } from 'react'
import { Row, Col, Input, Tag, Affix, Card, Divider, Spin, AutoComplete } from 'antd'
import Icon from '@ant-design/icons'
import { Route } from 'react-router-dom'
import { Base64 } from 'js-base64'
import mermaid from 'mermaid'

import Error from './Error'
import Preview from './Preview'
import pkg from 'mermaid/package.json'
import { base64ToState } from '../utils'

const mermaidVersion = pkg.version
const { Search } = Input

class PolyAutoComplete extends React.PureComponent {
    constructor (props) {
        super(props);
        this.state = {
            options: this.props.options,
            filtered_options: [],
            value: null,
        }
        console.log(`Options available: ${this.state.options}`)
    }

    searchResult = (query) => {
        //    console.log(`searching...`)
        var re = new RegExp(query, 'i')
        if (this.state.options === null) {
            return []
        }
        var vals = this.state.options.filter( function (v) {return re.test(v)})
        //    console.log(`results length: ${vals.length}`)
        return vals.map((item, idx) => {
        const category = `${query}${idx}`;
        return {
            value: item,
            label: (
                <div
                    style={{
                        display: 'block',
                        justifyContent: 'space-between',
                    }}
                >
                <span>
                    {item}{" \n"}
                </span>
                </div>
            ),
        };
        });
    }


    handleSearch = (query: string) => {
//            console.log(`handleSearch triggered. query: ${query}`)
        this.setState({filtered_options: query.length > 3 ? this.searchResult(query) : []})
//            this.state.filtered_options = query.length > 3 ? this.searchResult(query) : [];
    //        console.log(`results: ${this.state.filtered_options.length}`)
    };

    returnSelect = (value) => {
        console.log(`Child: Selected Value: ${value}`)
        this.props.onSelect(value)
    }


    render () {
        return (
            <Card title='Query' loading={this.props.loading}>
                  <AutoComplete
                        style={{ width: "100%", overflow: 'hidden' }}
                        //                value={this.state.value}
                        options={this.state.filtered_options}
                        onSelect={this.returnSelect}
                        onSearch={this.handleSearch}
                        placeholder="search item..."
                  />
             </Card>
        );
    }

}


class Edit extends React.Component {
  constructor (props) {
    super(props)

    this.onCodeChange = this.onCodeChange.bind(this)
    this.onMermaidConfigChange = this.onMermaidConfigChange.bind(this)
    this.onTriggerQuery = this.onTriggerQuery.bind(this)
    this.state = {
        options: null,
        filtered_options: null,
        value: null,
        spinner: false,
    }
    this.get_all_options();

    const {
      match: {
        params: { base64 }
          },
      location: { search }
      } = this.props
    this.json = base64ToState(base64, search)
    mermaid.initialize(this.json.mermaid)
  }

  toggleSpinner = () => {
        this.setState({spinner: !this.state.spinner});
    }

  get_all_options () {
        var that = this
        fetch("/api/list_items",
        {headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              }
        }
        ).then(function(res) {
            let a = res.clone()
            console.log(a.text())
            return res.json()

        })
//        res => res.json())
        .then(function(data) {
            console.log("Printing all Items: ")
            console.log(data)
            that.setState({options: data['all']})
//            that.options = data['all'];
        });

  }

  onTriggerQuery (value) {
//    console.log(`Options: ${this.state.options[0]}`)
//    console.log(`Options: ${this.state.options[0].includes('AL') ? 'Includes AL' : 'Does not include AL'}`)
    var that = this  // Necessary for inner functions to access this
    const {
      history,
      match: { path }
    } = this.props
    var result = ''
//    console.log(value)
//    console.log(`item=${encodeURIComponent(value)}`)
    fetch(`/api/search?item=${encodeURIComponent(value)}`, 
            {headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
              }
            }
        ).then( res => res.json()).then(data => data['data']).then( function(result) {

              const result_final = 
              `graph TD
              ${result}`
              // result = "Graph TD\n".concat(result)
              console.log(result_final)
              that.json.code = result_final.replace(/[' ']{2,}/g, '').replace("\\n","\n\t")
              console.log(JSON.stringify(that.json))
              const base64 = Base64.encodeURI(JSON.stringify(that.json))
              history.push(path.replace(':base64', base64))
              that.toggleSpinner()
          });
  }

  onCodeChange (event) {
    const {
      history,
      match: { path }
    } = this.props
    console.log('Code change')
    this.json.code = event.target.value
    const base64 = Base64.encodeURI(JSON.stringify(this.json))
    history.push(path.replace(':base64', base64))
  }

  onSelect = (value) => {
    console.log(`value selected: ${value}`)
//    this.setState({value: value})
    this.onTriggerQuery(value)

  }

  onKeyDown (event) {
    const keyCode = event.keyCode || event.which

    // 9 is key code for TAB
    if (keyCode === 9) {
      event.preventDefault()
      const TAB_SIZE = 4
      document.execCommand('insertText', false, ' '.repeat(TAB_SIZE))
    }
  }

  onMermaidConfigChange (event) {
    const str = event.target.value
    const {
      history,
      match: { path, url }
    } = this.props
    try {
      const config = JSON.parse(str)
      mermaid.initialize(config)
      this.json.mermaid = config
      const base64 = Base64.encodeURI(JSON.stringify(this.json))
      history.push(path.replace(':base64', base64))
    } catch (e) {
      const base64 = Base64.encodeURI(e.message)
      history.push(`${url}/error/${base64}`)
    }
  }

    //Asynch Wait before rendering Child Elements: https://stackoverflow.com/questions/34423419/passing-asynchronously-acquired-data-to-child-props
    //Passing Data between parent & child: https://towardsdatascience.com/passing-data-between-react-components-parent-children-siblings-a64f89e24ecf


  render () {
    const {
      match: { url }
    } = this.props
    return (
      <div>
        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
          <h1>PolycraftWorld Crafting</h1>
        </div>
        <Divider />
        <Row gutter={16}>
          <Col span={8}>
            <Affix>
                {this.state.options === null ?
                    <Card title="Loading..." loading={true}></Card>
                    : <PolyAutoComplete options={this.state.options} onSelect={this.onSelect} loading={false} />
                }
              <Card title='Mermaid Markdown' size='small'>
                <Input.TextArea
                  autoSize={{ minRows: 6, maxRows: 12 }}
                  id="code_input"
                  value={this.json.code}
                  onChange={this.onCodeChange}
                  onKeyDown={this.onKeyDown}
                />
              </Card>
            <Card title='Links' size='small'>
              <ul className='marketing-links'>
                <li>
                  <a href='https://polycraft.utdallas.edu' target='_blank' rel="noopener noreferrer">
                    <Icon type='book' /> PolycraftWorld Documentation
                  </a>
                </li>
                <li>
                  <a href='https://github.com/knsv/mermaid' target='_blank' rel="noopener noreferrer">
                    <Icon type='github' /> Powered by Mermaid
                  </a>
                </li>
              </ul>
            </Card>
            </Affix>
          </Col>
          <Col span={16}>
            <Spin spinning={this.state.spinner}>
            <Route
              exact
              path={url}
              render={props => <Preview {...props} code={this.json.code} toggleSpin={this.toggleSpinner} />}
            />
            </Spin>
            <Route path={url + '/error/:base64'} component={Error} />
            <h3 style={{ textAlign: 'right' }}>
              Powered by mermaid <Tag color='green'>{mermaidVersion}</Tag>
            </h3>
          </Col>
        </Row>
      </div>
    )
  }
}

export default Edit
