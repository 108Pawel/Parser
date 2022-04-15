# frozen_string_literal: true

require 'rspec'
require './parser'
require './laboratory_test_result'

describe Parser do
  parser = Parser.new

  describe '#get_result' do
    context 'when result is an integer' do
      let(:result) { 15 }
      it 'returns a boolean' do
        expect(parser.send(:get_result, result)).to eq(15.0)
      end
    end

    context 'when result is a bool' do
      let(:result) { 15.0 }
      it 'returns a boolean' do
        expect(parser.send(:get_result, result)).to eq(15.0)
      end
    end

    context 'when result is negative' do
      let(:result) { 'NEGATIVE' }
      it 'returns -1' do
        expect(parser.send(:get_result, result)).to eq(-1.0)
      end
    end

    context 'when result is positive' do
      let(:result) { '+' }
      it 'returns -2.0' do
        expect(parser.send(:get_result, result)).to eq(-2.0)
      end
    end

    context 'when result is +++' do
      let(:result) { '+++' }
      it 'returns -2.0' do
        expect(parser.send(:get_result, result)).to eq(-3.0)
      end
    end

    context 'when result dont match' do
      let(:result) { 'incorrect data' }
      it 'returns nil' do
        expect(parser.send(:get_result, result)).to eq(nil)
      end
    end
  end

  describe '#get_format' do
    context 'when format includes "A"' do
      let(:format) { 'A100' }
      it 'returns string "boolean"' do
        expect(parser.send(:get_format, format)).to eq('boolean')
      end
    end

    context 'when format includes "B"' do
      let(:format) { 'B200' }
      it 'returns "nil_3plus"' do
        expect(parser.send(:get_format, format)).to eq('nil_3plus')
      end
    end

    context 'when format includes "C"' do
      let(:format) { 'C250' }
      it 'returns "float"' do
        expect(parser.send(:get_format, format)).to eq('float')
      end
    end

    context 'when none of the required formats are present' do
      let(:format) { 'incorrect data' }
      it 'returns nil' do
        expect(parser.send(:get_format, format)).to eq(nil)
      end
    end
  end

  describe '#get_comment' do
    context 'when single comment is present' do
      let(:element) { [['OBX', '4', 'B250', '++'], ['NTE', '4', 'Comment 2 for ++ result']] }
      it 'returns a valid comment' do
        expect(parser.send(:get_comment, element)).to eq("Comment 2 for ++ result\n")
      end
    end

    context 'when many comments are present' do
      let(:element) do
        [['OBX', '4', 'B250', '++'], ['NTE', '4', 'Comment 1 for + result'], ['NTE', '4', 'Comment 2 for ++ result']]
      end
      it 'returns a valid composed comment' do
        expect(parser.send(:get_comment, element)).to eq("Comment 1 for + result\nComment 2 for ++ result\n")
      end
    end

    context 'when there are no comments are present' do
      let(:element) { [['OBX', '4', 'B250', '++']] }
      it 'returns a valid composed comment' do
        expect(parser.send(:get_comment, element)).to eq(nil)
      end
    end
  end

  describe '#map_single_result' do
    context 'without stubbed method calls' do
      let(:element) { [['OBX', '4', 'A100', '+'], ['NTE', '4', 'Comment 1 for + result']] }
      let(:expected_result) do
        { code: 'A100', result: -2.0, format: 'boolean', comment: "Comment 1 for + result\n" }
      end
      it 'maps correctly' do
        expect(parser.send(:map_single_result, element)).to eq(expected_result)
      end
    end

    context 'with stubbed method calls' do
      before do
        allow(parser).to receive(:get_format).with(any_args).and_return('boolean')
        allow(parser).to receive(:get_result).with(any_args).and_return(10.0)
        allow(parser).to receive(:get_comment).with(any_args).and_return('Comment')
      end

      let(:element) { [['OBX', '4', 'A100', '+'], ['NTE', '4', 'Comment 1 for + result']] }
      let(:expected_result) { { code: 'A100', result: 10.0, format: 'boolean', comment: 'Comment' } }
      it 'maps correctly' do
        expect(parser.send(:map_single_result, element)).to eq(expected_result)
      end
    end
  end

  describe '#mapped_results' do
    let(:file) { './test.txt' }
    let(:expected_result) do
      { code: 'A100', result: -2.0, format: 'boolean', comment: "Comment 1 for + result\n" }
    end

    before do
      allow(parser).to receive(:map_single_result).with(any_args).and_return(expected_result)
    end

    it 'returns array of LaboratoryTestResult' do
      expect(parser).to receive(:map_single_result).twice

      expect(parser.send(:mapped_results, file)).to be_an_instance_of(Array)

      expect(parser.send(:mapped_results, file)).to all(be_an_instance_of(LaboratoryTestResult))
    end
  end
end